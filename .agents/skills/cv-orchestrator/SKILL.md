---
name: cv-orchestrator
description: >-
  Master pipeline orchestrator for tailoring and generating ATS-optimized LaTeX CVs from structured JSON profiles and job descriptions.
  Use this skill whenever the user wants to generate, adapt, or update their LaTeX CV using scripts/generate_cv.py, match a job description, or synchronize their master JSON profile.
---

# LaTeX CV Pipeline Orchestrator Skill

This skill orchestrates the end-to-end automation pipeline that converts structured candidate JSON data into a polished, compile-ready LaTeX CV conforming to Mohamed Amine Nasfi's single-page template.

---

## 1. System Architecture

```
                    ┌────────────────────────────┐
                    │      Target Job Advert     │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
┌─────────────────────────┐  ┌─────────────────────────────┐
│   data/cv_master.json   │─▶│        job-matcher          │ (Match Score & Gap Matrix)
└─────────────────────────┘  └──────────────┬──────────────┘
                                            │
                                            ▼
                             ┌─────────────────────────────┐
                             │  Tailored Config / Profile  │ (Track & Keyword Selection)
                             └──────────────┬──────────────┘
                                            │
                                            ▼
                             ┌─────────────────────────────┐
                             │  scripts/generate_cv.py     │ (Python LaTeX Builder)
                             └──────────────┬──────────────┘
                                            │
                                            ▼
                             ┌─────────────────────────────┐
                             │         cv_output.tex       │ (Compile-Ready LaTeX Document)
                             └─────────────────────────────┘
```

---

## 2. Core Components & File Registry

| Component | Path | Description |
| :--- | :--- | :--- |
| **Master Profile (Markdown)** | [`MASTER_PROFILE.md`](file:///c:/Users/Medam/Desktop/cv%20builder/MASTER_PROFILE.md) | Human-readable comprehensive single source of truth. |
| **Master Profile (JSON)** | [`data/cv_master.json`](file:///c:/Users/Medam/Desktop/cv%20builder/data/cv_master.json) | Structured data source powering the Python generator. |
| **Python Generator Script** | [`scripts/generate_cv.py`](file:///c:/Users/Medam/Desktop/cv%20builder/scripts/generate_cv.py) | CLI script that converts JSON data to LaTeX code with escaping. |
| **LaTeX Reference Template** | [`.agents/skills/cv-builder/resources/templates/latex_cv_template.tex`](file:///c:/Users/Medam/Desktop/cv%20builder/.agents/skills/cv-builder/resources/templates/latex_cv_template.tex) | Baseline LaTeX template with `#2563EB` blue accent styling. |
| **Job Matcher Skill** | [`.agents/skills/job-matcher/SKILL.md`](file:///c:/Users/Medam/Desktop/cv%20builder/.agents/skills/job-matcher/SKILL.md) | Scoring rubric, equivalency map, and gap assessment. |
| **CV Guidelines Skill** | [`.agents/skills/cv-builder/SKILL.md`](file:///c:/Users/Medam/Desktop/cv%20builder/.agents/skills/cv-builder/SKILL.md) | Harvard action verbs, ATS guidelines, Prospects/NCS standards. |

---

## 3. End-to-End Orchestration Workflow

When the user asks to generate or adapt a CV:

### Step 1: Ingest Opportunity & Run Match Analysis
1. Read the target Job Description (JD).
2. **Language Detection**:
   - If the job description is in English $\to$ set `--lang en`.
   - If the job description is in French $\to$ set `--lang fr`.
3. Execute the `job-matcher` workflow:
   - Compute the weighted compatibility score (0 – 100%).
   - Produce the 4-tier match matrix (🟢 Direct Matches, 🟡 Transferable, 🔴 Hard Gaps).
   - Select the target track:
     * `it_support`: IT Support / Helpdesk / Systems & Networks
     * `fullstack`: Software Engineering / Full-Stack Web / DevOps
     * `custom`: Tailored hybrid configuration.

### Step 2: Tailor Experience to the JD (honest match only)
**Never invent employers, tools, dates, metrics, or certifications.** Source of truth: `MASTER_PROFILE.md` + `data/cv_master.json`.

1. Map JD must-haves → real experience ids / bullets that already prove them (or closest transferable work).
2. Keep **2–4 experiences** and **2–3 bullets** each — drop roles that dilute the match.
3. Rewrite subtitle + summary with the JD's role language, using only confirmed facts.
4. Reorder skills (5–7 categories) and keep **0–2** projects that support the offer.
5. Omit forbidden claims (AD/GPO, NVR/DVR hands-on, named network vendors as configured gear, POS peripherals, M365 admin, "véhiculé", Java/ML engineer claims).
6. Persist either as `data/tailored/<company>_<role>.json` **or** one-shot CLI overrides (`--subtitle`, `--summary`, `--exp`, `--projects`, `--skills-file`).

**1-page content budget:** short summary · ≤4 experiences · ≤3 bullets/role · ≤2 projects · compact skills. If the PDF overflows, cut before shipping.

### Step 3: Execute the Python Generator Script & Compile PDF
Run the generator using PowerShell / shell (compiles directly to PDF into `output/`):

```powershell
# For existing track (in French or English)
python scripts/generate_cv.py --input data/cv_master.json --track [it_support|fullstack] --lang [fr|en] --outdir output

# For custom tailored profile
python scripts/generate_cv.py --input data/tailored/target_role.json --track [track_name] --lang [fr|en] --outdir output

# One-shot override (no new JSON file)
python scripts/generate_cv.py --track it_support --lang fr --output Name_Role_FR --subtitle "..." --summary "..." --exp id1 id2 id3 --projects idA
```

Compilation **fails** if the PDF is not exactly **1 page** (use `--allow-multipage` only while debugging overflow).

### Step 4: Verification & Pre-Submission Audit
1. **Single-Page Constraint (hard)**: PDF page count must be **1**. If not, trim and regenerate.
2. **Honest JD alignment**: every bullet maps to a real task/tool from the master profile and echoes a JD theme — no invented keywords.
3. **LaTeX Escaping**: special characters (`%`, `&`, `$`, `#`, `_`) escaped by the generator.
4. **No First-Person Pronouns**: zero `je`, `moi`, `mon`, `I`, `me`, `my`.
5. **Action Verb Lead-Ins**: every bullet starts with an active verb from [`action_verbs.md`](file:///c:/Users/Medam/Desktop/cv%20builder/.agents/skills/cv-builder/references/action_verbs.md).
6. **Unicode / ATS**: `\input{glyphtounicode}` active; spot-check extracted text.

### Step 5: Deliver Output to User
1. Report the PDF path under `output/cv/<name>/` and confirm 1-page + language.
2. Briefly list which experiences were selected and why they match the JD (honest mapping).
3. Mention hard gaps for interview prep — do not paper over them on the CV.
4. Cover letter only if the user explicitly asks.
