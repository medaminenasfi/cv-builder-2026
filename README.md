# 📄 Automated LaTeX CV Builder & Job Matcher Engine

An automated, ATS-optimized **Curriculum Vitae (CV) & Resume generation system** tailored for **Mohamed Amine Nasfi**. 

The system maintains a single source of truth (SSOT) across dual career tracks, evaluates job descriptions with a 4-dimensional matching algorithm, and automatically renders and compiles single-page LaTeX resumes directly into **PDF** in either **English** or **French**.

---

## 🚀 Key Features

* **Dual-Track Specialization**:
  * **Track A — Full-Stack & DevOps**: MERN stack (React, Node.js, Express, MongoDB), Next.js, NestJS, TypeScript, PostgreSQL, Flutter, Docker, Nginx, Linux VPS, GitHub Actions CI/CD.
  * **Track B — IT Support & Systems/Network**: Windows 10/11 diagnostics, hardware assembly/maintenance, structured Ethernet cabling, IP CCTV deployment, router configuration, user support (L1/L2).
* **Automatic Language Adaptation**:
  * Detects Job Description language and generates the CV in **French** or **English** (`--lang fr` / `--lang en`).
  * Translates all section titles, summaries, subtitles, and highlights seamlessly.
* **Automatic Local PDF Compilation**:
  * Built-in portable **Tectonic** compiler in `bin/` compiles `.tex` files to PDF on the fly.
  * No manual LaTeX installation or cloud upload required.
* **Dedicated Results Directory (`output/`)**:
  * All generated `.tex` and `.pdf` files are automatically organized inside the `output/` folder.
* **ATS-Optimized LaTeX Template**:
  * Custom `#2563EB` blue accent headers, compact single-page layout (9pt, 0.55in margins).
  * Safe Unicode mapping (`glyphtounicode`) ensuring 100% text readability by Applicant Tracking Systems.
* **Antigravity Skills Ecosystem**:
  * `cv-builder`: Industry standards from **Prospects UK**, **National Careers Service**, and **Harvard FAS**.
  * `job-matcher`: 4-dimension weighted compatibility scoring (0–100%) and gap matrix.
  * `cv-orchestrator`: End-to-end pipeline automation.

---

## 📁 Repository Structure

```text
cv-builder/
├── data/
│   └── cv_master.json                    # Bilingual master profile data (JSON SSOT)
├── scripts/
│   └── generate_cv.py                    # Python script that renders LaTeX and compiles PDF
├── bin/
│   └── tectonic.exe                      # Standalone, portable LaTeX-to-PDF compiler
├── output/                               # Generated results — one folder per CV
│   ├── Mohamed_Amine_Nasfi_CV_IT_Support_FR/
│   │   ├── Mohamed_Amine_Nasfi_CV_IT_Support_FR.pdf
│   │   └── Mohamed_Amine_Nasfi_CV_IT_Support_FR.tex
│   ├── Mohamed_Amine_Nasfi_CV_FullStack_EN/
│   │   ├── Mohamed_Amine_Nasfi_CV_FullStack_EN.pdf
│   │   └── Mohamed_Amine_Nasfi_CV_FullStack_EN.tex
│   └── ...                               # every build creates its own named folder
├── MASTER_PROFILE.md                     # Comprehensive human-readable master profile
├── .agents/skills/
│   ├── cv-builder/                       # Harvard / Prospects / NCS career standards & templates
│   ├── job-matcher/                      # 4-tier match matrix & scoring rubric
│   └── cv-orchestrator/                  # Master pipeline orchestration skill
└── README.md                             # Documentation & user manual
```

---

## 🛠️ How to Use

### 1. Generating Default CVs (CLI)

Run the Python generator script from the project root:

```powershell
# 🇫🇷 French - IT Support & Maintenance CV (Outputs to output/*.pdf)
python scripts/generate_cv.py --track it_support --lang fr

# 🇬🇧 English - IT Support & Maintenance CV
python scripts/generate_cv.py --track it_support --lang en

# 🇫🇷 French - Full-Stack Developer & DevOps CV
python scripts/generate_cv.py --track fullstack --lang fr

# 🇬🇧 English - Full-Stack Software Engineer CV
python scripts/generate_cv.py --track fullstack --lang en
```

### 2. Command Line Arguments

| Flag | Short | Default | Description |
| :--- | :---: | :---: | :--- |
| `--input` | `-i` | `data/cv_master.json` | Path to the source JSON file. |
| `--track` | `-t` | `it_support` | Profile track (`it_support` or `fullstack`). |
| `--lang` | `-l` | `fr` | Target language (`fr` for French, `en` for English). |
| `--output` | `-o` | Auto-named | Custom filename (e.g. `My_Custom_CV.tex`). |
| `--outdir` | | `output` | Target folder — each build creates its own subfolder named after the CV. |
| `--compile`| `-c` | `True` | Automatically runs Tectonic to build `.pdf`. |

---

## 🎯 How the AI Agent Workflow Works

Whenever you provide a **Job Description (JD)** or job posting URL:

```
┌────────────────────────────────────────────────────────┐
│ 1. Language Detection & Role Analysis                  │
│    • Determines whether the JD is in French or English │
│    • Extracts must-haves, keywords, and stack          │
├────────────────────────────────────────────────────────┤
│ 2. Job-Matcher Compatibility Score (0 - 100%)          │
│    • Computes weighted fit across 4 dimensions:        │
│      - Hard Skills & Stack (40%)                       │
│      - Experience Level (25%)                          │
│      - DevOps, Systems & Methodologies (20%)           │
│      - Language & Logistics (15%)                      │
│    • Flags 🟢 Direct Matches, 🟡 Bridges, 🔴 Gaps      │
├────────────────────────────────────────────────────────┤
│ 3. Automated Adaptation & PDF Generation               │
│    • Customizes subtitle and summary hook              │
│    • Selects the top 2-3 portfolio projects            │
│    • Re-orders skills to maximize ATS match score      │
│    • Runs generate_cv.py to compile PDF into output/   │
└────────────────────────────────────────────────────────┘
```

---

## 📑 Core Standards Enforced

1. **Title**: The candidate's **Full Name** is always the title; never written as "CV" or "Resume".
2. **Third-Person Narrative**: Strictly zero occurrences of first-person pronouns (`I`, `me`, `je`, `moi`).
3. **Harvard Action Verbs**: Every bullet point begins with a dynamic power verb (*Spearheaded, Diagnosed, Engineered, Orchestrated*).
4. **Quantified Impact (STAR Formula)**: Bullet points contain measurable metrics (e.g. `\textbf{70\%}`).
5. **Privacy & Fair Hiring**: Excludes date of birth, photo, gender, marital status, and nationality.
