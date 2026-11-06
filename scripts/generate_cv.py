#!/usr/bin/env python3
"""
generate_cv.py
Generates an ATS-optimized, high-density LaTeX CV from structured JSON data,
and compiles it into PDF using the portable Tectonic compiler.
Supports both French (--lang fr) and English (--lang en).
Outputs all results to the output/ directory.
"""

import json
import os
import re
import shutil
import subprocess
import argparse
import sys
import unicodedata
import zlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Track key -> filename fragment used for default output names
TRACK_LABELS = {"it_support": "IT_Support", "fullstack": "FullStack", "tailored": "Tailored"}

# Section header translations
SECTION_TITLES = {
    "fr": {
        "summary": "Résumé",
        "experience": "Expérience",
        "skills": "Compétences Techniques",
        "projects": "Projets",
        "education": "Formation",
        "languages": "Langues"
    },
    "en": {
        "summary": "Summary",
        "experience": "Experience",
        "skills": "Technical Skills",
        "projects": "Projects",
        "education": "Education",
        "languages": "Languages"
    }
}


LATEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
LATEX_SPECIAL = re.compile("([" + re.escape("".join(LATEX_REPLACEMENTS)) + "])")


def escape_plain(text: str) -> str:
    escaped = LATEX_SPECIAL.sub(lambda m: LATEX_REPLACEMENTS[m.group(1)], text)
    # Tectonic runs XeTeX, where font-level ligature disabling is unavailable with the
    # bundled fonts; a zero-width glue keeps "ff" out of the ligature glyph so ATS text
    # extraction reads "Office", not U+FB00.
    return escaped.replace("ff", r"f\hspace{0pt}f")


def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters while preserving markdown bold (**bold**).
    """
    if not text:
        return ""

    bold_spans = []

    def stash(match):
        bold_spans.append(match.group(1))
        return f"\x00{len(bold_spans) - 1}\x00"

    text = re.sub(r"\*\*(.+?)\*\*", stash, text)
    text = escape_plain(text)

    for idx, bold_content in enumerate(bold_spans):
        text = text.replace(f"\x00{idx}\x00", f"\\textbf{{{escape_plain(bold_content)}}}")

    return text.replace("·", r"\textperiodcentered{}")


def get_field(obj: dict, key: str, lang: str, default: str = "") -> str:
    """
    Extracts a field that might be a plain string or a bilingual dict {fr: ..., en: ...}.
    """
    val = obj.get(key, default)
    if isinstance(val, dict):
        return val.get(lang, val.get("fr", default))
    return val if val else default


def get_language_section(content: dict, lang: str, label: str) -> dict:
    """
    Returns the requested language block, warning loudly when it falls back to French.
    """
    if isinstance(content.get(lang), dict):
        return content[lang]
    if isinstance(content.get("fr"), dict):
        print(f"Warning: no '{lang}' content for {label}, using French instead.", file=sys.stderr)
        return content["fr"]
    return content


MONTH_TOKENS = {
    "jan": 1, "janv": 1, "feb": 2, "fev": 2, "fevr": 2, "mar": 3, "apr": 4, "avr": 4,
    "may": 5, "mai": 5, "jun": 6, "juin": 6, "jul": 7, "juil": 7, "aug": 8, "aou": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

DATE_START = re.compile(r"([a-z]{3,6})\.?\s+((?:19|20)\d{2})")


def experience_start_key(exp: dict, lang: str):
    """
    Parses the leading "Month Year" of an experience date range as a sort key,
    or returns None when the string is not a recognisable date.
    """
    for candidate in (lang, "fr", "en"):
        section = exp.get(candidate)
        dates = section.get("dates", "") if isinstance(section, dict) else ""
        if not dates:
            continue
        ascii_text = unicodedata.normalize("NFKD", dates).encode("ascii", "ignore").decode().lower()
        match = DATE_START.search(ascii_text)
        if match:
            month = MONTH_TOKENS.get(match.group(1)) or MONTH_TOKENS.get(match.group(1)[:3])
            if month:
                return (int(match.group(2)), month)
    return None


def sort_by_recency(experiences: list, lang: str) -> list:
    """
    Applies the reverse-chronological order ATS expects, but only when every
    selected experience has a parseable start date, so an unrecognised date
    string can never silently reshuffle a deliberately ordered profile.
    """
    keys = [experience_start_key(e, lang) for e in experiences]
    if not keys or None in keys:
        return experiences
    ordered = sorted(zip(keys, range(len(keys)), experiences), key=lambda t: (-t[0][0], -t[0][1], t[1]))
    return [exp for _, _, exp in ordered]


def _content_block(track_data: dict, lang: str) -> dict:
    """
    Returns the editable language block of a profile, creating it when the track has none.
    """
    for key in (lang, "fr"):
        if isinstance(track_data.get(key), dict):
            return track_data[key]
    return track_data.setdefault(lang, {})


def apply_overrides(
    data: dict,
    track_name: str,
    lang: str,
    subtitle: str = None,
    summary: str = None,
    skills_file: str = None,
    experience_ids: list = None,
    project_ids: list = None,
) -> list:
    """
    Tailors a track in memory so one command produces a job-specific CV, without writing
    a JSON profile per offer. Returns warnings for references that do not exist.
    """
    warnings = []
    track = data.setdefault("profiles", {}).setdefault(track_name, {})
    if not isinstance(track, dict):
        raise SystemExit(f"Error: profile '{track_name}' is not an object and cannot be tailored.")

    content = _content_block(track, lang)
    if subtitle:
        content["subtitle"] = subtitle
    if summary:
        content["summary"] = summary
    if skills_file:
        path = resolve_project_path(skills_file)
        if not path.exists():
            raise SystemExit(f"Error: skills file {path} does not exist.")
        content["skills"] = json.loads(path.read_text(encoding="utf-8"))

    known_exps = {e["id"] for e in data.get("experiences", []) if "id" in e}
    known_projects = {p["id"] for p in data.get("projects", []) if "id" in p}
    for key, ids, known, label in (
        ("experience_ids", experience_ids, known_exps, "experience"),
        ("project_ids", project_ids, known_projects, "project"),
    ):
        if ids is None:
            continue
        unknown = [i for i in ids if i not in known]
        if unknown:
            warnings.append(
                f"unknown {label} id(s) ignored: {', '.join(unknown)} "
                f"(available: {', '.join(sorted(known)) or 'none'})"
            )
        track[key] = [i for i in ids if i in known]

    return warnings


def build_latex_document(data: dict, track_name: str = "it_support", lang: str = "fr") -> str:
    """
    Renders the complete LaTeX document string from parsed JSON.
    """
    labels = SECTION_TITLES.get(lang, SECTION_TITLES["fr"])

    personal = data.get("personal_info", {})
    profiles = data.get("profiles", {})
    track_data = profiles.get(track_name, {})
    if not track_data:
        raise SystemExit(
            f"Error: profile '{track_name}' not found. Available profiles: {', '.join(sorted(profiles)) or 'none'}"
        )

    # Extract bilingual profile config
    profile_content = get_language_section(track_data, lang, f"profile '{track_name}'")

    name = personal.get("name", "Mohamed Amine Nasfi")
    subtitle = profile_content.get("subtitle", "")
    phone = personal.get("phone", "")
    email = personal.get("email", "")
    location = get_field(personal, "location", lang)
    links = personal.get("links", [])

    # Format header links
    link_items = []
    for l in links:
        l_name = escape_latex(l.get("name", ""))
        l_url = l.get("url", "")
        link_items.append(f"\\href{{{l_url}}}{{\\underline{{{l_name}}}}}")
    links_str = " $\\quad|\\quad$ ".join(link_items)

    # Format summary
    summary_text = escape_latex(profile_content.get("summary", ""))

    # Format experiences
    all_exps = {e["id"]: e for e in data.get("experiences", []) if "id" in e}
    active_exp_ids = track_data.get("experience_ids", [e["id"] for e in data.get("experiences", [])])
    
    selected_exps = sort_by_recency([all_exps[eid] for eid in active_exp_ids if eid in all_exps], lang)

    exp_blocks = []
    for exp in selected_exps:
        exp_info = get_language_section(exp, lang, f"experience '{exp.get('id', '')}'")

        exp_title = escape_latex(exp_info.get("title", ""))
        exp_dates = escape_latex(exp_info.get("dates", ""))
        exp_company = escape_latex(exp.get("company", exp_info.get("company", "")))
        exp_location = escape_latex(exp_info.get("location", ""))

        items = []
        for hl in exp_info.get("highlights", []):
            items.append(f"      \\resumeItem{{{escape_latex(hl)}}}")
        items_str = "\n".join(items)

        block = f"""  \\resumeSubheading{{{exp_title}}}{{{exp_dates}}}{{{exp_company}}}{{{exp_location}}}
    \\resumeItemListStart
{items_str}
    \\resumeItemListEnd"""
        exp_blocks.append(block)

    experiences_str = "\n\n".join(exp_blocks)

    # Format skills
    skills_list = profile_content.get("skills", [])
    skills_items = []
    for sk in skills_list:
        cat = escape_latex(sk.get("category", ""))
        items = escape_latex(sk.get("items", ""))
        skills_items.append(f"  \\item \\textbf{{{cat}:}} {items}")
    skills_str = "\n".join(skills_items)

    # Format projects
    all_projects = {p["id"]: p for p in data.get("projects", []) if "id" in p}
    active_proj_ids = track_data.get("project_ids", [p["id"] for p in data.get("projects", [])])
    selected_projects = [all_projects[pid] for pid in active_proj_ids if pid in all_projects]

    proj_blocks = []
    for proj in selected_projects:
        proj_info = get_language_section(proj, lang, f"project '{proj.get('id', '')}'")

        p_title = escape_latex(proj_info.get("title", ""))
        p_tech = escape_latex(proj.get("tech", ""))
        p_desc = escape_latex(proj_info.get("description", ""))

        block = f"""  \\resumeProjectHeading{{\\textbf{{{p_title}}} $\\quad$ --- $\\quad$ \\emph{{\\color{{greytext}}{p_tech}}}}}{{}}
    \\resumeProjectListStart
      \\resumeItem{{{p_desc}}}
    \\resumeProjectListEnd"""
        proj_blocks.append(block)

    projects_str = "\n\n".join(proj_blocks)
    projects_section = (
        f"""% ---------- PROJECTS ----------
\\section{{{labels["projects"]}}}
\\resumeSubHeadingListStart

{projects_str}

\\resumeSubHeadingListEnd\\vspace{{-3pt}}
"""
        if projects_str
        else ""
    )

    # Format education
    edu_blocks = []
    for edu in data.get("education", []):
        edu_info = get_language_section(edu, lang, f"education '{edu.get('institution', '')}'")

        degree = escape_latex(edu_info.get("degree", ""))
        dates = escape_latex(edu_info.get("dates", ""))
        institution = escape_latex(edu.get("institution", ""))
        loc = escape_latex(edu_info.get("location", ""))
        edu_blocks.append(f"  \\resumeSubheading{{{degree}}}{{{dates}}}{{{institution}}}{{{loc}}}")
    education_str = "\n".join(edu_blocks)

    # Format languages
    lang_data = data.get("languages", {})
    if isinstance(lang_data, dict):
        selected_langs = lang_data.get(lang, lang_data.get("fr", []))
    else:
        selected_langs = lang_data

    lang_items = []
    for l_entry in selected_langs:
        l_name = escape_latex(l_entry.get("name", ""))
        l_level = escape_latex(l_entry.get("level", ""))
        lang_items.append(f"{l_name} ({l_level})")
    languages_str = " \\textperiodcentered{} ".join(lang_items)

    escaped_subtitle = escape_latex(subtitle)

    latex_code = f"""\\documentclass[letterpaper,9pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{xcolor}}
\\usepackage{{enumitem}}
\\usepackage[colorlinks=true]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage{{tabularx}}
\\usepackage{{iftex}}
\\ifPDFTeX
  \\input{{glyphtounicode}}
  \\pdfgentounicode=1
  \\usepackage{{microtype}}
  \\DisableLigatures[f]{{encoding = *, family = *}}
\\else
  \\usepackage{{fontspec}}
  \\setmainfont{{lmroman10-regular.otf}}[
    BoldFont=lmroman10-bold.otf,
    ItalicFont=lmroman10-italic.otf,
    BoldItalicFont=lmroman10-bolditalic.otf,
    SmallCapsFont=lmromancaps10-regular.otf,
    Ligatures=NoCommon]
\\fi

% Blue accent matching the Word version (#2563EB)
\\definecolor{{accent}}{{HTML}}{{2563EB}}
\\definecolor{{navy}}{{HTML}}{{1F2937}}
\\definecolor{{greytext}}{{HTML}}{{555555}}

\\hypersetup{{
  linkcolor=accent,
  urlcolor=accent,
  citecolor=accent,
}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

% Margins
\\addtolength{{\\oddsidemargin}}{{-0.55in}}
\\addtolength{{\\evensidemargin}}{{-0.55in}}
\\addtolength{{\\textwidth}}{{1.1in}}
\\addtolength{{\\topmargin}}{{-0.6in}}
\\addtolength{{\\textheight}}{{1.3in}}

\\urlstyle{{same}}
\\raggedright
\\raggedbottom
\\setlength{{\\tabcolsep}}{{0in}}

% Section titles — blue, matching Word headers
\\titleformat{{\\section}}{{
  \\vspace{{-1pt}}\\color{{accent}}\\scshape\\raggedright\\large
}}{{}}{{0em}}{{}}[\\color{{accent}}\\titlerule \\vspace{{-1pt}}]
\\titlespacing*{{\\section}}{{0pt}}{{6pt}}{{4pt}}

% Custom commands
\\newcommand{{\\resumeItem}}[1]{{\\item\\small{{#1}}}}
\\newcommand{{\\resumeSubheading}}[4]{{
  \\vspace{{-1pt}}\\item
  \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\textbf{{#1}} & \\textit{{\\color{{greytext}}#2}} \\\\
    \\textit{{\\small\\color{{greytext}} #3}} & \\textit{{\\small\\color{{greytext}} #4}}
  \\end{{tabular*}}\\vspace{{-2pt}}
}}
\\newcommand{{\\resumeProjectHeading}}[2]{{
  \\item
  \\begin{{tabular*}}{{0.97\\textwidth}}{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\small #1 & #2
  \\end{{tabular*}}\\vspace{{-1pt}}
}}

\\newcommand{{\\resumeSubHeadingListStart}}{{\\begin{{itemize}}[leftmargin=0.18in, label={{}}, itemsep=1.2pt, topsep=2.5pt, parsep=0pt]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}\\vspace{{-2pt}}}}

\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}[leftmargin=0.24in, label={{}}, itemsep=0.9pt, topsep=1.2pt, parsep=0pt]}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{-2pt}}}}

\\newcommand{{\\resumeProjectListStart}}{{\\begin{{itemize}}[leftmargin=0.24in, label={{}}, itemsep=0.9pt, topsep=1.2pt, parsep=0pt]}}
\\newcommand{{\\resumeProjectListEnd}}{{\\end{{itemize}}\\vspace{{-2pt}}}}

\\newcommand{{\\resumeLangHeading}}[2]{{
  \\vspace{{-1pt}}\\item
  \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
    \\textbf{{#1}} & #2
  \\end{{tabular*}}\\vspace{{-1pt}}
}}

\\begin{{document}}

% ---------- HEADER ----------
\\begin{{center}}
    \\textbf{{\\Huge \\color{{navy}} {escape_latex(name)}}} \\\\[3pt]
    \\small \\textbf{{\\color{{accent}} {escaped_subtitle}}} \\\\[3pt]
    \\footnotesize \\color{{greytext}}
    {escape_latex(phone)} $\\quad|\\quad$
    \\href{{mailto:{email}}}{{\\underline{{{escape_latex(email)}}}}} $\\quad|\\quad$
    {escape_latex(location)} \\\\[2pt]
    {links_str}
\\end{{center}}
\\vspace{{-5pt}}

% ---------- SUMMARY ----------
\\section{{{labels["summary"]}}}
\\begin{{itemize}}[leftmargin=0.18in, label={{}}, itemsep=1.2pt, topsep=1.5pt, parsep=0pt]
\\item \\footnotesize{{{summary_text}}}
\\end{{itemize}}\\vspace{{-3pt}}

% ---------- EXPERIENCE ----------
\\section{{{labels["experience"]}}}
\\resumeSubHeadingListStart

{experiences_str}

\\resumeSubHeadingListEnd\\vspace{{-2pt}}

% ---------- TECHNICAL SKILLS ----------
\\section{{{labels["skills"]}}}
\\begin{{itemize}}[leftmargin=0.18in, label={{}}, topsep=2pt, itemsep=1pt, parsep=0pt]
\\footnotesize{{
{skills_str}
}}
\\end{{itemize}}\\vspace{{-3pt}}

{projects_section}
% ---------- EDUCATION ----------
\\section{{{labels["education"]}}}
\\resumeSubHeadingListStart
{education_str}
\\resumeSubHeadingListEnd\\vspace{{-1pt}}

% ---------- LANGUAGES ----------
\\section{{{labels["languages"]}}}
\\begin{{itemize}}[leftmargin=0.18in, label={{}}, topsep=2pt, itemsep=1pt, parsep=0pt]
\\footnotesize{{
  \\item {languages_str}
}}
\\end{{itemize}}

\\end{{document}}
"""
    return latex_code


TEX_ENGINES = ("tectonic", "xelatex", "pdflatex")


def is_runnable(path: Path) -> bool:
    if not path.is_file() or not os.access(path, os.X_OK):
        return False
    if sys.platform == "win32":
        return True
    # A Windows binary copied into a Unix checkout is present but unusable.
    with path.open("rb") as handle:
        return handle.read(2) != b"MZ"


def resolve_tex_engine(explicit: str = None) -> Path:
    """
    Finds a usable LaTeX engine: CLI override, TEX_ENGINE env var, project bin/, then PATH.
    """
    tried = []

    if explicit:
        tried.append(Path(explicit))
    if os.environ.get("TEX_ENGINE"):
        tried.append(Path(os.environ["TEX_ENGINE"]))

    for name in TEX_ENGINES:
        for suffix in ("", ".exe"):
            tried.append(PROJECT_ROOT / "bin" / (name + suffix))
        found = shutil.which(name)
        if found:
            tried.append(Path(found))

    for candidate in tried:
        if is_runnable(candidate):
            return candidate

    raise SystemExit(
        "Error: no usable LaTeX engine found. Tried:\n  "
        + "\n  ".join(str(c) for c in tried)
        + "\nInstall Tectonic (https://tectonic-typesetting.github.io) or a TeX distribution, "
        "or point --tex-engine / TEX_ENGINE at a binary."
    )


def engine_command(engine: Path, tex_path: Path, output_dir: Path) -> list:
    if engine.stem.lower().startswith("tectonic"):
        return [str(engine), str(tex_path), "--outdir", str(output_dir)]
    return [
        str(engine),
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={output_dir}",
        str(tex_path),
    ]


def compile_pdf(tex_path: Path, output_dir: Path, tex_engine: str = None) -> bool:
    """
    Compiles the .tex file into a .pdf file. Returns False and reports the failure loudly on stderr.
    """
    engine = resolve_tex_engine(tex_engine)
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = engine_command(engine, tex_path, output_dir)
    print(f"Compiling PDF with {engine}: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Compilation FAILED (exit {e.returncode}):", file=sys.stderr)
        print((e.stdout or "")[-800:] or (e.stderr or "")[-800:], file=sys.stderr)
        return False
    except OSError as e:
        print(f"Compilation FAILED: could not run {engine}: {e}", file=sys.stderr)
        return False

    print("Compilation successful!")
    return True


PAGE_OBJECT_RE = re.compile(rb"/Type\s*/Page(?![s\w])")
PDFINFO_PAGES_RE = re.compile(r"^Pages:\s+(\d+)\s*$", re.MULTILINE)


def _count_page_objects(blob: bytes) -> int:
    return len(PAGE_OBJECT_RE.findall(blob))


def _inflate_pdf_streams(raw: bytes) -> bytes:
    """
    Best-effort FlateDecode inflate so compressed object streams become searchable.
    Tectonic/xdvipdfmx PDFs usually hide /Type/Page inside compressed streams.
    """
    chunks = []
    for part in re.split(rb"stream\r?\n", raw)[1:]:
        data = part.split(rb"endstream", 1)[0]
        if data.endswith(b"\r\n"):
            data = data[:-2]
        elif data.endswith(b"\n"):
            data = data[:-1]
        try:
            chunks.append(zlib.decompress(data))
        except zlib.error:
            continue
    return b"\n".join(chunks)


def pdf_page_count(path: Path) -> int:
    """
    Counts pages in a PDF without third-party packages.
    Order: pdfinfo (if installed) → inflated stream scan → raw byte scan.
    """
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        try:
            info = subprocess.run(
                [pdfinfo, str(path)],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            match = PDFINFO_PAGES_RE.search(info or "")
            if match:
                return int(match.group(1))
        except (OSError, subprocess.CalledProcessError, ValueError):
            pass

    raw = path.read_bytes()
    for blob in (_inflate_pdf_streams(raw), raw):
        pages = _count_page_objects(blob)
        if pages:
            return pages
    return 0


def assert_single_page_cv(pdf_path: Path) -> bool:
    """
    Enforces the project rule: every CV PDF must be exactly one page.
    """
    try:
        pages = pdf_page_count(pdf_path)
    except OSError as e:
        print(f"Error: could not read PDF page count for {pdf_path}: {e}", file=sys.stderr)
        return False
    if pages == 1:
        return True
    if pages == 0:
        print(
            f"Error: could not determine page count for {pdf_path}. "
            "Install poppler-utils (pdfinfo) or rebuild; use --allow-multipage only for debugging.",
            file=sys.stderr,
        )
        return False
    print(
        f"Error: CV must be exactly 1 page (got {pages}). "
        "Trim experiences, bullets, projects or skills and rebuild. "
        "Use --allow-multipage only for debugging.",
        file=sys.stderr,
    )
    return False


def resolve_project_path(raw: str) -> Path:
    """
    Accepts a path relative to the current directory or to the repository root.
    """
    path = Path(raw)
    if path.is_absolute() or path.exists():
        return path
    root_relative = PROJECT_ROOT / path
    return root_relative if root_relative.exists() else path


def add_compiler_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--no-compile", action="store_true", help="Write the .tex file only, skip PDF compilation")
    parser.add_argument("--tex-engine", default=None, help="Path to tectonic/xelatex/pdflatex (default: auto-detect)")
    parser.add_argument(
        "--allow-multipage",
        action="store_true",
        help="Debug only: allow CV PDFs longer than 1 page (default rejects them)",
    )


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX and PDF CV from JSON data.")
    parser.add_argument("--input", "-i", default="data/cv_master.json", help="Path to input JSON file")
    parser.add_argument("--output", "-o", default=None, help="Name of output .tex file (saved into output/)")
    parser.add_argument("--track", "-t", default="it_support", choices=sorted(TRACK_LABELS), help="Profile track to render")
    parser.add_argument("--lang", "-l", default="fr", choices=["fr", "en"], help="Language: 'fr' or 'en'")
    parser.add_argument("--outdir", default="output", help="Directory where results are stored")
    parser.add_argument("--subtitle", default=None, help="Override the profile subtitle for this job")
    parser.add_argument("--summary", default=None, help="Override the profile summary for this job")
    parser.add_argument("--skills-file", default=None, help="Path to a JSON array of {category, items} skill lines")
    parser.add_argument("--exp", nargs="*", default=None, help="Experience ids to include, in order")
    parser.add_argument("--projects", nargs="*", default=None, help="Project ids to include, in order")
    add_compiler_arguments(parser)
    args = parser.parse_args()

    input_path = resolve_project_path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.", file=sys.stderr)
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for warning in apply_overrides(
        data,
        track_name=args.track,
        lang=args.lang,
        subtitle=args.subtitle,
        summary=args.summary,
        skills_file=args.skills_file,
        experience_ids=args.exp,
        project_ids=args.projects,
    ):
        print(f"Warning: {warning}", file=sys.stderr)

    # Determine output file name
    outdir = resolve_project_path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.output:
        tex_filename = args.output if args.output.endswith(".tex") else f"{args.output}.tex"
    else:
        lang_suffix = "EN" if args.lang == "en" else "FR"
        track_suffix = TRACK_LABELS[args.track]
        tex_filename = f"Mohamed_Amine_Nasfi_CV_{track_suffix}_{lang_suffix}.tex"

    # Type-first layout: output/cv/<CV-name>/ for CVs, output/cover_letter/<name>/ for letters
    cv_dir = outdir / "cv" / Path(tex_filename).stem
    cv_dir.mkdir(parents=True, exist_ok=True)
    tex_path = cv_dir / tex_filename

    # Build LaTeX code
    latex_content = build_latex_document(data, track_name=args.track, lang=args.lang)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    print(f"Generated LaTeX CV at: {tex_path.resolve()} (Track: {args.track}, Lang: {args.lang})")

    # Compile to PDF
    if not args.no_compile:
        pdf_path = tex_path.with_suffix(".pdf")
        if not compile_pdf(tex_path, cv_dir, args.tex_engine):
            return 1
        if not pdf_path.exists():
            print(f"Error: compiler reported success but {pdf_path} is missing.", file=sys.stderr)
            return 1
        if not args.allow_multipage and not assert_single_page_cv(pdf_path):
            return 1
        print(f"Generated PDF CV at: {pdf_path.resolve()}")

    return 0


if __name__ == "__main__":
    exit(main())
