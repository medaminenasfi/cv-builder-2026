# 📄 Automated LaTeX CV & Cover Letter Builder + Job Matcher Engine

An automated, ATS-optimized **application generation system** tailored for **Mohamed Amine Nasfi**.

The system maintains a single source of truth (SSOT) across dual career tracks, evaluates job descriptions with a 4-dimensional matching algorithm, and automatically renders and compiles single-page **CVs** and **cover letters** directly into **PDF** in either **English** or **French** — with matching visual identity.

---

## 🚀 Key Features

* **Dual-Track Specialization**:
  * **Track A — Full-Stack & DevOps**: React, Next.js, Node.js, Express, NestJS, TypeScript, PostgreSQL, MongoDB, Flutter, Docker, Nginx, Linux VPS, GitHub Actions CI/CD.
  * **Track B — IT Support & Systems/Network**: Windows 10/11 diagnostics, hardware assembly/maintenance, structured Ethernet cabling, IP CCTV deployment, router configuration, user support (L1/L2).
* **Automatic Language Adaptation**:
  * Detects the job description language and generates documents in **French** or **English** (`--lang fr` / `--lang en`).
  * Translates all section titles, summaries, subtitles, and highlights seamlessly.
* **CV + Cover Letter in One Identity**:
  * The cover-letter letterhead (name, accent line, contacts) reuses the CV header style — CV and letter read as one package.
  * Letter content is structured JSON (`objet`, `salutation`, `paragraphs`, `closing`) rendered to LaTeX and compiled like the CV.
* **Automatic Local PDF Compilation**:
  * Built-in portable **Tectonic** compiler in `bin/` compiles `.tex` to PDF on the fly.
  * No manual LaTeX installation or cloud upload required.
* **Type-First Results Layout (`output/`)**:
  * `output/cv/<name>/` for CVs, `output/cover_letter/<name>/` for letters — one subfolder per job application.
* **ATS-Optimized Templates**:
  * Custom `#2563EB` blue accent headers, compact single-page CV layout (9pt).
  * Safe Unicode mapping (`glyphtounicode`) + XeTeX `Ligatures=NoCommon` — no `ﬁ` ligatures, 100% readable text for Applicant Tracking Systems.
* **Skills Ecosystem (`.agents/skills/`)**:
  * `cv-builder`: Industry standards from **Prospects UK**, **National Careers Service**, and **Harvard FAS**.
  * `job-matcher`: 4-dimension weighted compatibility scoring (0–100%), gap matrix, honest-gap rules.
  * `cv-orchestrator`: End-to-end pipeline automation (URL → score → CV PDF).
  * `cover-letter`: JD-targeted letter generation (EN + FR lettre de motivation) — **explicit request only**.

---

## 📁 Repository Structure

```text
cv-builder/
├── data/
│   ├── cv_master.json                    # Bilingual master profile (JSON SSOT) — it_support + fullstack tracks
│   ├── tailored/                         # Per-posting tailored CV profiles (e.g. lip_belgique_web_dev.json)
│   └── letters/                          # Per-posting cover-letter content (e.g. socomec_support_it.json)
├── scripts/
│   ├── generate_cv.py                    # Renders LaTeX CV → compiles PDF (output/cv/<name>/)
│   └── generate_cover_letter.py          # Renders LaTeX cover letter → compiles PDF (output/cover_letter/<name>/)
├── bin/
│   └── tectonic.exe                      # Standalone, portable LaTeX-to-PDF compiler
├── output/                               # Type-first: one subfolder per job application
│   ├── cv/
│   │   ├── Mohamed_Amine_Nasfi_CV_LIP_WebDev_FR/
│   │   │   ├── Mohamed_Amine_Nasfi_CV_LIP_WebDev_FR.pdf
│   │   │   └── Mohamed_Amine_Nasfi_CV_LIP_WebDev_FR.tex
│   │   └── ...                           # every CV build creates its own named subfolder
│   └── cover_letter/
│       └── Socomec_Support_IT_FR/
│           ├── cover_letter_fr.pdf
│           ├── cover_letter_fr.tex
│           └── lettre_motivation_fr.md   # plain-text paste-ready version
├── MASTER_PROFILE.md                     # Comprehensive human-readable master profile
├── .agents/skills/
│   ├── cv-builder/                       # Harvard / Prospects / NCS career standards & templates
│   ├── job-matcher/                      # 4-tier match matrix & scoring rubric
│   ├── cv-orchestrator/                  # Master pipeline orchestration skill
│   └── cover-letter/                     # Letter method (5 sources), QA checklist, FR conventions
└── README.md                             # Documentation & user manual
```

---

## 🛠️ How to Use

### 1. Generating CVs (CLI)

Run from the project root:

```powershell
# 🇫🇷 French — IT Support & Maintenance CV
python scripts/generate_cv.py --track it_support --lang fr

# 🇬🇧 English — Full-Stack Developer & DevOps CV
python scripts/generate_cv.py --track fullstack --lang en

# 🎯 Tailored CV from a per-posting profile (data/tailored/*.json)
python scripts/generate_cv.py --input data/tailored/lip_belgique_web_dev.json --track tailored --lang fr --output Mohamed_Amine_Nasfi_CV_LIP_WebDev_FR
```

**CV flags**

| Flag | Short | Default | Description |
| :--- | :---: | :---: | :--- |
| `--input` | `-i` | `data/cv_master.json` | Source JSON file. |
| `--track` | `-t` | `it_support` | `it_support`, `fullstack`, or `tailored`. |
| `--lang` | `-l` | `fr` | `fr` or `en`. |
| `--output` | `-o` | Auto-named | Custom filename (without folder → lands in `output/cv/<name>/`). |
| `--outdir` | | `output` | Base output folder (subfolders `cv/` auto-created). |
| `--compile` | `-c` | `True` | Automatically runs Tectonic to build the PDF. |

### 2. Generating Cover Letters (CLI)

Letter content lives in `data/letters/<name>.json`:

```json
{
  "personal_info": { "name": "...", "phone": "...", "email": "...", "location": { "fr": "...", "en": "..." } },
  "letters": {
    "fr": {
      "subtitle": "Technicien Support IT | Développeur Full-Stack",
      "company": "Socomec Group",
      "company_address": "ZI Chebedda, 1135 Ben Arous, Tunisie",
      "place": "Gabès",
      "objet": "Candidature au poste de Technicien support IT – Site de Ben Arous (offre n° 117)",
      "salutation": "Madame, Monsieur,",
      "paragraphs": [ "...", "..." ],
      "closing": "Dans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées."
    }
  }
}
```

Generate the PDF (date line auto-inserted in the letter's language):

```powershell
python scripts/generate_cover_letter.py --input data/letters/socomec_support_it.json --lang fr --name Socomec_Support_IT_FR
```

**Letter flags**

| Flag | Short | Default | Description |
| :--- | :---: | :---: | :--- |
| `--input` | `-i` | *(required)* | Letter JSON file in `data/letters/`. |
| `--lang` | `-l` | `fr` | `fr` or `en` (falls back to `fr` content if the key is missing). |
| `--name` | `-n` | Input file stem | Subfolder name under `output/cover_letter/`. |
| `--outdir` | | `output` | Base output folder. |
| `--compile` | `-c` | `True` | Automatically runs Tectonic to build the PDF. |

### 3. Paste-Ready Markdown

Every letter also ships as a `.md` next to its PDF (portals with plain-text boxes). Letters follow the
`cover-letter` skill: 3–4 paragraphs, ≤ 400 words, the JD's own vocabulary, top-2 requirements matched with
numbered proofs, one honest gap bridge, formule de politesse for French.

---

## 🤖 How the AI Agent Workflow Works

Whenever you provide a **job posting URL**:

```
┌────────────────────────────────────────────────────────┐
│ 1. Fetch & Analyze the Job Description                 │
│    • Handles site blocks (Hellowork direct, WTTJ /     │
│      LinkedIn / Indeed via browser or mirrors)         │
│    • Extracts must-haves, keywords, stack, language    │
├────────────────────────────────────────────────────────┤
│ 2. Job-Matcher Compatibility Score (0 - 100%)          │
│    • Weighted across 4 dimensions:                     │
│      - Hard Skills & Stack (40%)                       │
│      - Experience Level (25%)                          │
│      - DevOps, Systems & Methodologies (20%)           │
│      - Language & Logistics (15%)                      │
│    • Flags 🟢 Direct Matches, 🟡 Bridges, 🔴 Gaps      │
│    • Tier 3 (<60%) or hard disqualifier → honest       │
│      advice, NO CV built                               │
├────────────────────────────────────────────────────────┤
│ 3. Automated CV Adaptation & PDF Generation            │
│    • Customizes subtitle and summary hook              │
│    • Selects the top 2-3 portfolio projects            │
│    • Re-orders skills to maximize ATS match            │
│    • data/tailored/<job>.json → generate_cv.py         │
│    • → output/cv/<name>/<name>.pdf (+ score report)    │
└────────────────────────────────────────────────────────┘
```

**Cover letters are a separate, explicit step** — they are never auto-generated with a CV build. Ask for
"cover letter" / "lettre de motivation" and the `cover-letter` skill runs:

```
JD + tailored profile → match table (top 2-3) → company research (1 value + 1 topical)
→ data/letters/<job>.json → generate_cover_letter.py → output/cover_letter/<name>/
```

---

## 📑 Core Standards Enforced

**CV**
1. **Title**: The candidate's **Full Name** is always the title; never written as "CV" or "Resume".
2. **Third-Person Narrative**: Strictly zero first-person pronouns (`I`, `me`, `je`, `moi`).
3. **Harvard Action Verbs**: Every bullet begins with a dynamic power verb (*Spearheaded, Diagnosed, Engineered*).
4. **Quantified Impact (STAR)**: Bullets contain measurable metrics (e.g. `\textbf{70\%}`).
5. **Privacy & Fair Hiring**: Excludes date of birth, photo, gender, marital status, and nationality.

**Cover letter**
6. **Honesty**: real numbers only, gaps bridged truthfully, never invented skills or metrics.
7. **One page**: ≤ ~400 words, recipient named when findable (FR default `Madame, Monsieur,`).
8. **JD vocabulary**: reuse the posting's exact terms (human readers + ATS keyword match).

**Verification (every PDF, both types)**
9. Single page · ligature-free (`U+FB01` absent) · JD-keyword extraction against the text layer ·
   no first-person pronouns in CVs.
