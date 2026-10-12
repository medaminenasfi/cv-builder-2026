#!/usr/bin/env python3
"""
generate_cv.py
Generates an ATS-optimized, high-density LaTeX CV from structured JSON data,
and compiles it into PDF using the portable Tectonic compiler.
Supports both French (--lang fr) and English (--lang en).
Outputs all results to the output/ directory.
"""

import json
import re
import os
import subprocess
import argparse
from pathlib import Path

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


def escape_latex(text: str) -> str:
    """
    Escapes LaTeX special characters while preserving markdown bold (**bold**) and deliberate syntax.
    """
    if not text:
        return ""
    
    # 1. Preserve markdown bold: **text** -> temporary placeholder
    bold_matches = []
    def save_bold(match):
        bold_matches.append(match.group(1))
        return f"BOLDTOKENXYZ{len(bold_matches)-1}ENDTOKEN"

    text = re.sub(r"\*\*(.+?)\*\*", save_bold, text)

    # 2. Escape reserved LaTeX characters
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
    ]
    for char, escaped in replacements:
        text = text.replace(char, escaped)

    # 3. Restore bold tokens as \textbf{...}
    for idx, bold_content in enumerate(bold_matches):
        escaped_bold = bold_content
        for char, escaped in replacements:
            escaped_bold = escaped_bold.replace(char, escaped)
        text = text.replace(f"BOLDTOKENXYZ{idx}ENDTOKEN", f"\\textbf{{{escaped_bold}}}")

    # Convert bullet dots
    text = text.replace("·", r"\textperiodcentered{}")

    return text


def get_field(obj: dict, key: str, lang: str, default: str = "") -> str:
    """
    Extracts a field that might be a plain string or a bilingual dict {fr: ..., en: ...}.
    """
    val = obj.get(key, default)
    if isinstance(val, dict):
        return val.get(lang, val.get("fr", default))
    return val if val else default


def build_latex_document(data: dict, track_name: str = "it_support", lang: str = "fr") -> str:
    """
    Renders the complete LaTeX document string from parsed JSON.
    """
    labels = SECTION_TITLES.get(lang, SECTION_TITLES["fr"])

    personal = data.get("personal_info", {})
    profiles = data.get("profiles", {})
    track_data = profiles.get(track_name, {})

    # Extract bilingual profile config
    if lang in track_data:
        profile_content = track_data[lang]
    elif "fr" in track_data:
        profile_content = track_data["fr"]
    else:
        profile_content = track_data

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
    
    selected_exps = [all_exps[eid] for eid in active_exp_ids if eid in all_exps]

    exp_blocks = []
    for exp in selected_exps:
        # Check if experience has language-specific sub-dict
        if lang in exp:
            exp_info = exp[lang]
        elif "fr" in exp:
            exp_info = exp["fr"]
        else:
            exp_info = exp

        exp_title = escape_latex(exp_info.get("title", ""))
        exp_dates = escape_latex(exp_info.get("dates", ""))
        exp_company = escape_latex(exp.get("company", exp_info.get("company", "")))
        exp_location = escape_latex(exp_info.get("location", ""))

        exp_title = exp_title.replace("---", "---").replace("--", "--")
        exp_dates = exp_dates.replace("---", "---").replace("--", "--")

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
        if lang in proj:
            proj_info = proj[lang]
        elif "fr" in proj:
            proj_info = proj["fr"]
        else:
            proj_info = proj

        p_title = escape_latex(proj_info.get("title", ""))
        p_tech = escape_latex(proj.get("tech", ""))
        p_desc = escape_latex(proj_info.get("description", ""))

        block = f"""  \\resumeProjectHeading{{\\textbf{{{p_title}}} $\\quad$ --- $\\quad$ \\emph{{\\color{{greytext}}{p_tech}}}}}{{}}
    \\resumeProjectListStart
      \\resumeItem{{{p_desc}}}
    \\resumeProjectListEnd"""
        proj_blocks.append(block)

    projects_str = "\n\n".join(proj_blocks)

    # Format education
    edu_blocks = []
    for edu in data.get("education", []):
        if lang in edu:
            edu_info = edu[lang]
        elif "fr" in edu:
            edu_info = edu["fr"]
        else:
            edu_info = edu

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

    escaped_subtitle = escape_latex(subtitle).replace(r"\|", "|")

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
  \\defaultfontfeatures{{Ligatures=NoCommon}}
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
    \\textbf{{\\Huge \\scshape \\color{{navy}} {escape_latex(name)}}} \\\\[3pt]
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

% ---------- PROJECTS ----------
\\section{{{labels["projects"]}}}
\\resumeSubHeadingListStart

{projects_str}

\\resumeSubHeadingListEnd\\vspace{{-3pt}}

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


def compile_with_tectonic(tex_path: Path, output_dir: Path) -> bool:
    """
    Compiles the .tex file into a .pdf file using bin/tectonic.exe.
    """
    # Look for tectonic in bin/ or system PATH
    tectonic_bin = Path("bin/tectonic.exe")
    if not tectonic_bin.exists():
        tectonic_bin = Path("tectonic")

    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [str(tectonic_bin), str(tex_path), "--outdir", str(output_dir)]
    print(f"Compiling PDF: {' '.join(cmd)}")
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Compilation successful!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Compilation warning/error: {e}")
        if hasattr(e, "stderr") and e.stderr:
            print(f"Details: {e.stderr[:300]}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX and PDF CV from JSON data.")
    parser.add_argument("--input", "-i", default="data/cv_master.json", help="Path to input JSON file")
    parser.add_argument("--output", "-o", default=None, help="Name of output .tex file (saved into output/)")
    parser.add_argument("--track", "-t", default="it_support", choices=["it_support", "fullstack", "tailored"], help="Profile track to render")
    parser.add_argument("--lang", "-l", default="fr", choices=["fr", "en"], help="Language: 'fr' or 'en'")
    parser.add_argument("--compile", "-c", action="store_true", default=True, help="Automatically compile to PDF")
    parser.add_argument("--outdir", default="output", help="Directory where results are stored")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Determine output file name
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.output:
        tex_filename = args.output if args.output.endswith(".tex") else f"{args.output}.tex"
    else:
        lang_suffix = "EN" if args.lang == "en" else "FR"
        track_suffix = "IT_Support" if args.track == "it_support" else "FullStack"
        tex_filename = f"Mohamed_Amine_Nasfi_CV_{track_suffix}_{lang_suffix}.tex"

    # Each CV gets its own subfolder inside outdir (folder name = CV name)
    cv_dir = outdir / Path(tex_filename).stem
    cv_dir.mkdir(parents=True, exist_ok=True)
    tex_path = cv_dir / tex_filename

    # Build LaTeX code
    latex_content = build_latex_document(data, track_name=args.track, lang=args.lang)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    print(f"Generated LaTeX CV at: {tex_path.resolve()} (Track: {args.track}, Lang: {args.lang})")

    # Compile to PDF
    if args.compile:
        pdf_success = compile_with_tectonic(tex_path, cv_dir)
        pdf_path = tex_path.with_suffix(".pdf")
        if pdf_success and pdf_path.exists():
            print(f"Generated PDF CV at: {pdf_path.resolve()}")

    return 0


if __name__ == "__main__":
    exit(main())
