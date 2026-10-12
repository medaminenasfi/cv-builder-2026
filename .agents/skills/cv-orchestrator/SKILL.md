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

### Step 2: Prepare Tailored JSON Configuration
- If the role fits an existing profile track (`it_support` or `fullstack`), select that track key with the detected language.
- If the role requires custom tailoring:
  1. Create a specialized JSON file in `data/tailored/<company>_<role>.json`.
  2. Adapt the `subtitle` to match the exact target title.
  3. Refine the `summary` to emphasize relevant achievements.
  4. Select the most relevant 2–3 `projects` and re-order `skills`.

### Step 3: Execute the Python Generator Script & Compile PDF
Run the generator using PowerShell / shell (compiles directly to PDF into `output/`):

```powershell
# For existing track (in French or English)
python scripts/generate_cv.py --input data/cv_master.json --track [it_support|fullstack] --lang [fr|en] --outdir output

# For custom tailored profile
python scripts/generate_cv.py --input data/tailored/target_role.json --track [track_name] --lang [fr|en] --outdir output
```

### Step 4: Verification & Pre-Submission Audit
Run the generated `.tex` file through the 6-point verification:
1. **Single-Page Constraint**: Ensure bullet point and section spacing fits comfortably on 1 page (9pt font, 0.55in margins).
2. **LaTeX Escaping**: Verify that all special characters (`%`, `&`, `$`, `#`, `_`) are properly escaped.
3. **No First-Person Pronouns**: Verify zero occurrences of `je`, `moi`, `mon`, `I`, `me`, `my`.
4. **Action Verb Lead-Ins**: Verify every bullet begins with an active verb from [`action_verbs.md`](file:///c:/Users/Medam/Desktop/cv%20builder/.agents/skills/cv-builder/references/action_verbs.md).
5. **Bold & Metrics**: Check that impact numbers (e.g., `\textbf{70\%}`) render clearly.
6. **Unicode Mapping**: Ensure `\input{glyphtounicode}` is active for ATS readability.

### Step 5: Deliver Output to User
1. Inform the user of the output `.tex` file path.
2. Present the complete `.tex` code in a clean code block for immediate copy-pasting into Overleaf.
3. Provide strategic interview talking points to address any gaps identified during the match phase.
