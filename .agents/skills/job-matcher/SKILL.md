---
name: job-matcher
description: >-
  Systematic framework for evaluating a target Job Description (JD) against the candidate's Master Profile.
  Use this skill whenever the user provides a job description, job offer, or role specification to assess compatibility,
  calculate match scores, identify skill gaps, determine track alignment, and generate tailored application strategies.
---

# Job Matcher & Gap Assessor Skill

This skill provides an objective, rigorous system for evaluating any job opportunity against the candidate's verified background in [MASTER_PROFILE.md](file:///c:/Users/Medam/Desktop/cv%20builder/MASTER_PROFILE.md).

It calculates quantitative fit metrics, categorizes skill overlaps, flags potential roadblocks, and produces an actionable roadmap for adapting the candidate's CV and interview positioning.

---

## 1. Assessment Philosophy & Objectives

1. **Objectivity First**: Never give false confidence or inflate match percentages. If a required qualification is absent, flag it clearly.
2. **Transferable Skills Recognition**: Distinguish between an absolute hard barrier (e.g. 5+ years of C++ when the candidate writes TypeScript/Python) and an adjacent transferable skill (e.g. Docker + Linux VPS knowledge bridging into basic Kubernetes/Cloud concepts).
3. **Track Identification**: Automatically identify whether the target role aligns with:
   - **Track A**: Software Engineering / Full-Stack Web / Mobile / DevOps
   - **Track B**: IT Support / Helpdesk / Systems & Network Administration
   - **Hybrid**: DevOps / Infrastructure Support / Internal Tools Engineering
4. **Actionable Output**: Always conclude with concrete recommendations for CV adaptation and interview strategy.

---

## 2. Quantitative Scoring Formula

The overall **Match Score (0 – 100%)** is calculated across 4 weighted dimensions:

$$\text{Match Score} = (H \times 0.40) + (E \times 0.25) + (T \times 0.20) + (L \times 0.15)$$

| Component | Weight | Criteria Evaluated |
| :--- | :---: | :--- |
| **$H$: Hard Skills & Core Tech Stack** | **40%** | Languages, primary frameworks, databases, and core operational domain knowledge (e.g., React, Node, PostgreSQL vs. Windows Support, Network Cabling). |
| **$E$: Experience Level & Seniority** | **25%** | Years of experience, autonomy, delivery track record (freelance client delivery, internship, PFE), team collaboration. |
| **$T$: DevOps, Systems & Methodologies** | **20%** | Docker, Linux, CI/CD, Git, Nginx, Agile Scrum, ticketing, diagnostics, SOP documentation. |
| **$L$: Language, Soft Skills & Practical Fit** | **15%** | French / English proficiency, customer facing / user support orientation, location (Tunisia / Remote / Relocation), work authorization. |

### Match Tier Classifications:
- **$\ge 80\%$ — Strong Match (Tier 1)**: High probability of securing an interview. Direct alignment with core requirements. Focus on precision keyword targeting.
- **$60\% - 79\%$ — Competitive Match (Tier 2)**: Viable candidate with 1–2 minor gaps. Strategy focuses on spotlighting transferable achievements and adjacent tooling.
- **$< 60\%$ — Reach / High-Gap (Tier 3)**: Major divergence from core criteria (e.g., requires senior 7+ years or unrelated technologies like Java Spring or Embedded C). Advise candidate clearly.

---

## 3. Step-by-Step Evaluation Workflow

```
┌─────────────────────────────────┐
│ 1. Parse & Ingest Job Advert    │  (Extract title, must-haves, nice-to-haves, stack)
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 2. Query Master Profile         │  (Cross-reference MASTER_PROFILE.md credentials)
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 3. 4-Tier Matrix Gap Analysis   │  (Direct Matches, Transferable, Missing, Risks)
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 4. Track Selection & Scoring    │  (Track A vs. Track B, compute 0–100% score)
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 5. Generate Assessment Report   │  (Deliver structured verdict & CV blueprint)
└─────────────────────────────────┘
```

### Step 1: Ingest & Deconstruct the Job Description
Extract and structure:
- **Target Role Title & Seniority**: (e.g., *Junior/Mid Développeur Full-Stack*, *Technicien Support N2*, *DevOps Engineer*).
- **Hard Requirements (Must-Have)**: Strict prerequisites mentioned in the description.
- **Preferred Qualifications (Nice-to-Have)**: Bonus skills, secondary frameworks.
- **Core Working Language**: French, English, or Bilingual.
- **Work Model**: On-site (location), Hybrid, or Full Remote.

### Step 2: Cross-Reference against [MASTER_PROFILE.md](file:///c:/Users/Medam/Desktop/cv%20builder/MASTER_PROFILE.md)
Check each extracted requirement against Mohamed Amine's verified profile:
- Primary stack (React/Next.js, Node/Express/NestJS, Python, PHP, PostgreSQL, MongoDB).
- IT Support capabilities (Windows 10/11, hardware troubleshooting, structured cabling, IP camera CCTV, router configuration).
- DevOps & Systems (Linux Debian/Ubuntu, Docker, Nginx, GitHub Actions, VPS).
- Projects catalog (ApplyFlow, Eventify, Rental ERP, Club Rendement+, GCT automation).
- Degree (Licence en Systèmes d'Information, Mention Très Bien).

### Step 3: Classify Findings into the 4 Match Buckets
1. **Direct Matches ($\checkmark$ Green)**: Skills and experiences present in both the JD and Master Profile.
2. **Transferable / Adjacent Matches ($\approx$ Yellow)**: Requirements where adjacent experience can credibly satisfy the need (e.g., JD asks for *AWS EC2*, candidate has *Linux VPS + Docker + Nginx*; JD asks for *MySQL*, candidate has *PostgreSQL + SQL*).
3. **Hard Gaps ($\times$ Red)**: Explicit must-haves that are completely absent from the profile.
4. **Logistical Risks / Questions ($\Delta$ Amber)**: Years of experience mismatch, location constraints, visa/work permit requirements.

### Step 4: Determine the Optimal CV Strategy
- Recommend the best **Track**:
  * *Track A (Full-Stack / DevOps)*
  * *Track B (IT Support / Systems & Network Admin)*
  * *Track C (Custom Hybrid)*
- Identify the **Top 3 Projects** from the Master Profile to feature prominently.
- Pinpoint **Key Phrasing & Keywords** to embed in the Summary and Experience sections.

---

## 4. Standardized Job Assessment Output Report

When presenting the evaluation to the user, strictly follow this layout:

```markdown
# 🎯 Job Fit & Gap Assessment: [Target Job Title] at [Company]

## 1. Executive Summary & Verdict
- **Overall Match Score**: **[Score]%** ([Tier: Strong Match / Competitive Match / Reach])
- **Recommended Profile Track**: [Track A: Full-Stack / Track B: IT Support / Hybrid]
- **Target Language**: [Français / English]
- **Verdict**: [1–2 sentences summarizing whether to apply and core application thesis]

---

## 2. Weighted Score Breakdown
- **Hard Skills & Tech Stack (40%)**: [Score]/40
- **Experience & Delivery Record (25%)**: [Score]/25
- **Systems, DevOps & Tools (20%)**: [Score]/20
- **Language & Soft Competencies (15%)**: [Score]/15

---

## 3. Detailed Skills Gap Matrix

| Category | Job Requirement | Candidate Profile Match | Status |
| :--- | :--- | :--- | :---: |
| **Language / Core** | [e.g., React.js / Node.js] | [Verified in 4+ client apps & Eventify] | 🟢 Direct Match |
| **Database** | [e.g., PostgreSQL] | [Core skill in Freelance & Eventify] | 🟢 Direct Match |
| **Cloud / Infra** | [e.g., AWS S3 / EC2] | [Linux VPS, Docker, Render, Nginx] | 🟡 Transferable |
| **Requirement** | [e.g., Kubernetes] | [Not present in Master Profile] | 🔴 Gap |

---

## 4. Strategic Positioning & Interview Defenses
- **How to Bridge Gaps**: [Actionable talking point to address missing skills]
- **Marquee Selling Points**: [The 2–3 strongest accomplishments that stand out for this role]

---

## 5. LaTeX CV Adaptation Blueprint
- **Suggested Subtitle**: `[Target Title] | [Top 3-4 Keywords]`
- **Summary Focus**: [What to highlight in the 3-4 sentence Résumé block]
- **Featured Projects**:
  1. [Project 1 name + rationale]
  2. [Project 2 name + rationale]
- **Skills Section Priority Order**: [Order of bullet lines under Compétences Techniques]
```

---

## 5. Seamless Transition to LaTeX CV Generation

Immediately after outputting the assessment report, prompt the user:
> *"Would you like me to generate your tailored single-page LaTeX CV for this position based on this blueprint?"*

If the user approves, proceed directly to tailoring [latex_cv_template.tex](file:///c:/Users/Medam/Desktop/cv%20builder/.agents/skills/cv-builder/resources/templates/latex_cv_template.tex) and outputting the compile-ready code.
