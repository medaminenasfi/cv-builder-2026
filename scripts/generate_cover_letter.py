import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_cv import compile_with_tectonic, escape_latex, get_field

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]


def format_date_line(lang: str, place: str) -> str:
    today = date.today()
    if lang == "fr":
        return f"{place}, le {today.day} {MOIS_FR[today.month - 1]} {today.year}"
    return f"{place}, {MONTHS_EN[today.month - 1]} {today.day}, {today.year}"


def build_letter_document(data: dict, lang: str) -> str:
    letters = data.get("letters", {})
    if lang in letters:
        letter = letters[lang]
    elif "fr" in letters:
        letter = letters["fr"]
    else:
        raise SystemExit("Error: no letter content found in input JSON.")

    personal = data.get("personal_info", {})
    name = escape_latex(personal.get("name", ""))
    phone = escape_latex(personal.get("phone", ""))
    email = personal.get("email", "")
    location = escape_latex(get_field(personal, "location", lang))
    subtitle = escape_latex(letter.get("subtitle", ""))
    company = escape_latex(letter.get("company", ""))
    company_address = escape_latex(letter.get("company_address", ""))
    place = escape_latex(letter.get("place", get_field(personal, "location", lang).split(",")[0]))
    objet = escape_latex(letter.get("objet", ""))
    salutation = escape_latex(letter.get("salutation", "Madame, Monsieur,"))
    closing = escape_latex(letter.get("closing", ""))

    paragraphs = []
    for para in letter.get("paragraphs", []):
        paragraphs.append(escape_latex(para))
    body = "\n\n".join(paragraphs)

    date_line = escape_latex(format_date_line(lang, letter.get("place", place)))

    recipient_block = ""
    if company:
        recipient_block = company
        if company_address:
            recipient_block += f" \\\\ {company_address}"

    objet_line = f"\\textbf{{Objet :}} {objet}" if lang == "fr" else f"\\textbf{{Subject:}} {objet}"

    latex_code = f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage[margin=2.4cm,noheadfoot]{{geometry}}
\\usepackage{{latexsym}}
\\usepackage{{xcolor}}
\\usepackage[colorlinks=true]{{hyperref}}
\\usepackage{{iftex}}
\\ifPDFTeX
  \\input{{glyphtounicode}}
  \\pdfgentounicode=1
  \\usepackage{{microtype}}
\\else
  \\usepackage{{fontspec}}
  \\defaultfontfeatures{{Ligatures=NoCommon}}
\\fi

\\definecolor{{accent}}{{HTML}}{{2563EB}}
\\definecolor{{navy}}{{HTML}}{{1F2937}}
\\definecolor{{greytext}}{{HTML}}{{555555}}

\\hypersetup{{
  linkcolor=accent,
  urlcolor=accent,
  citecolor=accent,
}}

\\pagestyle{{empty}}
\\setlength{{\\parindent}}{{0pt}}
\\setlength{{\\parskip}}{{7pt}}
\\urlstyle{{same}}

\\begin{{document}}

% ---------- LETTERHEAD (matches CV identity) ----------
\\begin{{center}}
    \\textbf{{\\Huge \\scshape \\color{{navy}} {name}}} \\\\[3pt]
    \\small \\textbf{{\\color{{accent}} {subtitle}}} \\\\[3pt]
    \\footnotesize \\color{{greytext}}
    {phone} $\\;|\\;$
    \\href{{mailto:{email}}}{{\\underline{{{escape_latex(email)}}}}} $\\;|\\;$
    {location}
\\end{{center}}

\\vspace{{8pt}}
\\hfill {date_line}

\\vspace{{12pt}}
{recipient_block}

\\vspace{{10pt}}
{objet_line}

\\vspace{{4pt}}
{salutation}

{body}

{closing}

\\vspace{{14pt}}
\\hfill \\textbf{{{name}}}

\\end{{document}}
"""
    return latex_code


def main():
    parser = argparse.ArgumentParser(description="Generate LaTeX and PDF cover letter from JSON data.")
    parser.add_argument("--input", "-i", required=True, help="Path to letter JSON file (data/letters/...)")
    parser.add_argument("--lang", "-l", default="fr", choices=["fr", "en"], help="Language: 'fr' or 'en'")
    parser.add_argument("--name", "-n", default=None, help="Application folder name (default: input file stem)")
    parser.add_argument("--compile", "-c", action="store_true", default=True, help="Automatically compile to PDF")
    parser.add_argument("--outdir", default="output", help="Base output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return 1

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    app_name = args.name or input_path.stem
    lang_suffix = "fr" if args.lang == "fr" else "en"

    letter_dir = Path(args.outdir) / "cover_letter" / app_name
    letter_dir.mkdir(parents=True, exist_ok=True)

    tex_filename = f"cover_letter_{lang_suffix}.tex"
    tex_path = letter_dir / tex_filename

    latex_content = build_letter_document(data, lang=args.lang)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    print(f"Generated LaTeX cover letter at: {tex_path.resolve()} (Lang: {args.lang})")

    if args.compile:
        if compile_with_tectonic(tex_path, letter_dir):
            pdf_path = tex_path.with_suffix(".pdf")
            if pdf_path.exists():
                print(f"Generated PDF cover letter at: {pdf_path.resolve()}")

    return 0


if __name__ == "__main__":
    exit(main())
