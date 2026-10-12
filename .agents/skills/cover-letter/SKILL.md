---
name: cover-letter
description: >-
  Generate a tailored cover letter (EN) or lettre de motivation (FR) for Mohamed Amine Nasfi from a job
  description, reusing the Master Profile and the tailored JSON already built for the CV. STRICT TRIGGER:
  use this skill ONLY when the user explicitly asks for a cover letter / lettre de motivation / letter.
  It is NEVER part of the default "build" pipeline — a job URL plus "build" produces the CV only.
---

# Cover Letter Generator Skill

Produces a one-page, JD-targeted cover letter in the same language as the job posting, consistent with
the candidate's verified profile ([MASTER_PROFILE.md](file:///c:/Users/Medam/Desktop/cv%20builder/MASTER_PROFILE.md))
and the honest-gap rules of the `job-matcher` skill.

## 0. Trigger Rule (critical)

- **Auto-trigger: NO.** The `cv-orchestrator` pipeline (job URL → score → CV PDF) runs **without** this skill.
- **Trigger only on explicit request**: "cover letter", "lettre de motivation", "write a letter", "motivation letter".
- If the user sends a job URL with no mention of a letter, do not offer one unprompted more than once.

## 1. Method — distilled from the 5 source guides

Sources and what each contributed (see [source_guides.md](references/source_guides.md) for the full distillation):

| Source | Key contribution |
| :--- | :--- |
| [National Careers Service (UK)](https://nationalcareers.service.gov.uk/careers-advice/covering-letter) | 3–5 paragraph frame; research the employer; STAR examples; one fresh letter per application |
| [UMich Career Center](https://careercenter.umich.edu/content/cover-letter-resources) | Paragraph-by-paragraph content; named recipient; no clichés; not every sentence starts with "I"; formatting specs |
| [r/datascience "Killer Cover Letter" guide](https://www.reddit.com/r/datascience/comments/tag8l5/my_guide_to_writing_a_killer_cover_letter/) | JD analysis → 2-column match table → hook / summary-with-numbers / top-2 skill matches via story themes / why-here (1 value + 1 topical) / close |
| [Indeed career advice](https://www.indeed.com/career-advice/resumes-cover-letters/how-to-write-a-cover-letter) | Consensus structure: header, salutation, opening hook, qualification body, closing CTA (site login-walled; structure only) |
| [Harvard FAS guide](https://careerservices.fas.harvard.edu/resources/harvard-college-guide-to-resumes-cover-letters/) | One page, professional tone, match CV details, error-free (page is a stub; minimal verified content) |

## 2. Workflow

```
┌────────────────────────────────────────────┐
│ 1. Explicit trigger confirmed?             │  (No letter unless the user asked)
└───────────────┬────────────────────────────┘
                ▼
┌────────────────────────────────────────────┐
│ 2. Gather inputs                           │  JD (fetched or pasted) + tailored JSON
│    (reuse data/tailored/<...>.json)        │  from the CV build; else master track
└───────────────┬────────────────────────────┘
                ▼
┌────────────────────────────────────────────┐
│ 3. Match table                             │  JD requirement | proof from profile
│    top 2–3 matches ONLY, JD's own words    │  (verified: projects, freelance, GCT)
└───────────────┬────────────────────────────┘
                ▼
┌────────────────────────────────────────────┐
│ 4. Company research                        │  mission, product, 1 value + 1 topical hook
└───────────────┬────────────────────────────┘
                ▼
┌────────────────────────────────────────────┐
│ 5. Draft in JD language (FR or EN)         │  structure per §3, ≤ 1 page
└───────────────┬────────────────────────────┘
                ▼
┌────────────────────────────────────────────┐
│ 6. QA checklist (§5) → deliver PDF + .md   │  output/cover_letter/<App-name>/
└────────────────────────────────────────────┘
```

## 3. Letter Structure

### English (3–4 paragraphs, 250–400 words)

1. **Hook** — who you are, the exact role, and one company-specific reason. If referred by someone, first sentence.
2. **Transition + summary statement** — one sentence with a number ("shipped 4 end-to-end client products…"),
   then a bridge ("Three things make me a strong fit for this role:").
3. **Top 2 skill matches** — the two most important JD requirements, each tied to a verified proof with a number
   (e.g., the 70% process-time reduction at GCT). Frame each match through a story theme: taking initiative,
   affinity for challenging work, dealing with failure, curiosity. Use the JD's own vocabulary ("Next.js", not
   "modern frameworks"). Address the ONE most likely objection (e.g., location, stack gap) in 1–2 honest sentences.
4. **Why this company + close** — one values-driven reason + one industry/topical reason, then a direct CTA
   (availability, interview request). Thank the reader.

### French — lettre de motivation (250–350 words)

1. **En-tête + Objet** — `Objet : Candidature au poste de [titre] – [référence si indiquée]`
2. **`Madame, Monsieur,`** (default; use a name only if verified)
3. **Accroche** — poste visé, où l'offre a été trouvée, une phrase d'accroche avec un chiffre.
4. **Corps 1 — adéquation poste/profil** — les 2 exigences clés du JD prouvées par des réalisations chiffrées,
   vocabulaire de l'annonce. Varier les débuts de phrases (pas de « Je … » systématique).
5. **Corps 2 — pour cette entreprise** — 1 valeur + 1 fait récent/sectoriel ; montrer que la candidature est ciblée.
6. **Conclusion + formule de politesse** — demande d'entretien + disponibilité, puis :
   `Dans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.`
7. Signature : prénom + nom.

## 4. Hard Rules (from all sources)

- **One page, ~250–400 words.** Every sentence earns its place: "half the words, twice the examples."
- **Never reuse a letter.** Fresh draft per posting; 5 tailored letters beat 50 generic ones.
- **Speak the employer's language**: reuse the JD's exact terms (also helps ATS keyword match).
- **Don't restate the CV** — add the *why* behind the facts, context the CV can't carry.
- **Named recipient** when findable (LinkedIn, posting); never "To Whom It May Concern"; FR default `Madame, Monsieur,`.
- **No clichés** ("make me an outstanding candidate"), no arrogance, active voice, confident but not imposing.
- **Vary sentence openings** — never start every sentence with "I" / "Je".
- **Error-free**: proofread pass mandatory; letters showcase writing ability.
- **Honesty (job-matcher rule)**: bridge gaps truthfully ("montée en compétence rapide visée sur X"), never invent
  experience, metrics, or familiarity. A letter is not the place to hide a disqualifier either.
- **Formatting**: same font/identity as the CV header; 10–12 pt; 0.5–1" margins; left-justified. If applying by
  email, the letter body IS the email text.

## 5. QA Checklist (all must pass before delivery)

- [ ] ≤ 1 page / ≤ ~400 words
- [ ] Role title + company named correctly (copy-paste check against the JD)
- [ ] Top 2 JD requirements each matched with a verified, numbered proof
- [ ] At least one company-specific sentence (values/product/news) — no generic praise
- [ ] Zero clichés; sentence openings varied; active voice
- [ ] No invented skills, dates, or metrics; consistent with the tailored JSON used for the CV
- [ ] Language matches the posting; FR formule de politesse present if French
- [ ] Deliverables in `output/cover_letter/<App-name>/`: `cover_letter_<lang>.pdf` (LaTeX, letterhead matches
      the CV identity), the `.tex`, and a paste-ready `.md` for portal text boxes
- [ ] Letter content JSON saved in `data/letters/<app-name>.json` (SSOT for regeneration)

## 6. Deliverable

1. **PDF letter** (default, like the CV): write the content JSON to `data/letters/<app-name>.json`, then run
   `python scripts/generate_cover_letter.py --input data/letters/<app-name>.json --lang <lang> --name <App-name>`
   → `output/cover_letter/<App-name>/cover_letter_<lang>.pdf`. The LaTeX letterhead reuses the CV identity
   (navy name, #2563EB accent, grey contact line) so CV + letter form one visual package.
2. **Paste-ready `.md`** of the same text in the same `cover_letter/<App-name>/` folder (portals with text boxes).
3. A 2–3 bullet note on the positioning choices made (top matches used, objection addressed) — nothing longer.

Type-first output layout: `output/cv/<App-name>/` (CV .tex+.pdf) + `output/cover_letter/<App-name>/`
(letter .tex+.pdf+.md). `generate_cv.py` writes into `cv/`, `generate_cover_letter.py` into `cover_letter/`.
