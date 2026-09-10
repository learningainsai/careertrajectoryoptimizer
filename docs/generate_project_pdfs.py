"""Generate the Career Trajectory Optimizer documentation set (flyer, setup
guide, technical brief, user guide) as polished, print-ready PDFs.

Pipeline: Python builds semantic HTML + embedded CSS for each document,
then a local headless Chrome instance prints each page to PDF. This keeps
layout (grids, gradients, shadows, flex) far richer than a canvas-drawing
approach, while staying fully offline (no weasyprint/playwright required —
just the Chrome binary already on the machine).

Structure mirrors the OrgPolicyChatBot doc generator (same design-system
pattern: gradient hero, pill badges, stat tiles, pipeline chips, cards,
gradient footer CTA) with a distinct palette and Career Trajectory
Optimizer-specific content.

Run:
    uv run python docs/generate_project_pdfs.py
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
HTML_DIR = DOCS_DIR / "html"
PDF_DIR = DOCS_DIR / "pdfs"
HTML_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]


# ---------------------------------------------------------------------------
# Design system — distinct palette from the reference material, reused
# structural pattern (gradient hero, pill badges, stat tiles, pipeline
# chips, two-column cards, gradient footer CTA) across all four documents.
# ---------------------------------------------------------------------------

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  color: #1B2430;
  background: #F5F7FA;
  -webkit-font-smoothing: antialiased;
}
:root {
  --ink: #0A1220;
  --ink2: #142A52;
  --teal: #2F5FD9;
  --teal-deep: #1E3A8A;
  --teal-light: #7FA6FF;
  --amber: #B45309;
  --amber-bg: #FDECD3;
  --emerald: #15803D;
  --emerald-bg: #DCFCE7;
  --rose: #BE123C;
  --rose-bg: #FDE1E7;
  --indigo: #6D28D9;
  --indigo-bg: #EDE6FB;
  --slate-900: #131C28;
  --slate-700: #33475A;
  --slate-500: #62788C;
  --slate-300: #D6E0E8;
  --slate-100: #EEF3F6;
  --card: #FFFFFF;
}
.page {
  width: 210mm;
  min-height: 296mm;
  background: #F5F7FA;
  position: relative;
  padding-bottom: 0mm;
}
.page + .page { page-break-before: always; }

/* ---------- hero ---------- */
.hero {
  background:
    radial-gradient(720px 420px at 88% -10%, rgba(127,166,255,0.35), transparent 60%),
    linear-gradient(135deg, var(--ink) 0%, var(--ink2) 48%, var(--teal-deep) 100%);
  color: #EAF0F3;
  padding: 6.5mm 14mm 4.3mm 14mm;
}
.hero-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 10mm; }
.brandmark { display: flex; align-items: center; gap: 2.6mm; }
.brand-badge {
  width: 10mm; height: 10mm; border-radius: 2.6mm;
  background: linear-gradient(155deg, var(--teal-light), var(--teal-deep));
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.35);
  flex-shrink: 0;
}
.brand-badge svg { width: 5.4mm; height: 5.4mm; }
.brand-name { font-size: 11.5pt; font-weight: 700; letter-spacing: 0.2px; color: #FFFFFF; }
.brand-sub { font-size: 7pt; color: #A9C1E8; letter-spacing: 1.6px; text-transform: uppercase; font-weight: 600; }
.kicker-pill {
  display: inline-flex; align-items: center; gap: 1.5mm;
  border: 1px solid rgba(255,255,255,0.28);
  background: rgba(255,255,255,0.08);
  border-radius: 20px; padding: 1.7mm 3.6mm;
  font-size: 7.2pt; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase;
  color: #DCE7F7; white-space: nowrap;
}
.hero-title { font-size: 19.5pt; font-weight: 800; line-height: 1.12; margin: 3.5mm 0 1.6mm 0; color: #FFFFFF; letter-spacing: -0.3px; }
.hero-tagline { font-size: 10.2pt; font-weight: 600; color: var(--teal-light); margin: 0 0 1.8mm 0; }
.hero-desc { font-size: 8.6pt; line-height: 1.44; color: #C9D6EA; max-width: 150mm; margin: 0 0 3mm 0; }
.chip-row { display: flex; flex-wrap: wrap; gap: 2mm; }
.chip {
  font-size: 7.2pt; font-weight: 600; color: #EAF1FF;
  background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.22);
  padding: 1.4mm 3.2mm; border-radius: 20px; letter-spacing: 0.2px;
}
.hero-meta {
  text-align: right; font-size: 7.6pt; color: #AFC0DC; line-height: 1.6; min-width: 46mm;
}
.hero-meta b { color: #FFFFFF; font-weight: 700; }

/* ---------- body ---------- */
.body-wrap { padding: 3.4mm 14mm 0 14mm; }
.section-label {
  display: flex; align-items: center; gap: 2.2mm;
  font-size: 8.6pt; font-weight: 800; color: var(--slate-900);
  text-transform: uppercase; letter-spacing: 0.5px;
  margin: 3mm 0 1.5mm 0;
}
.section-label .dot { width: 2.8mm; height: 2.8mm; border-radius: 1px; flex-shrink: 0; }
.dot-teal { background: var(--teal); }
.dot-amber { background: var(--amber); }
.dot-rose { background: var(--rose); }
.dot-emerald { background: var(--emerald); }
.dot-indigo { background: var(--indigo); }

.callout {
  border-radius: 2.6mm; padding: 2.2mm 4mm; font-size: 8pt; line-height: 1.34;
  border-left: 3px solid; margin-bottom: 1mm;
}
.callout-rose { background: var(--rose-bg); border-color: var(--rose); color: #6E1420; }
.callout-teal { background: #E7EEFC; border-color: var(--teal); color: #10254F; }
.callout-amber { background: var(--amber-bg); border-color: var(--amber); color: #5C3406; }
.callout b { font-weight: 700; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3mm; }
.grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 2.6mm; }

.card {
  background: var(--card); border-radius: 2.6mm; padding: 2mm 2.6mm;
  border: 1px solid var(--slate-300); border-top: 2.4px solid var(--teal);
  box-shadow: 0 1px 2px rgba(15,25,45,0.05);
}
.card.acc-amber { border-top-color: var(--amber); }
.card.acc-rose { border-top-color: var(--rose); }
.card.acc-emerald { border-top-color: var(--emerald); }
.card.acc-indigo { border-top-color: var(--indigo); }
.card-icon {
  width: 6.6mm; height: 6.6mm; border-radius: 1.8mm; display: flex; align-items: center; justify-content: center;
  background: #E7EEFC; margin-bottom: 1.6mm;
}
.card-icon svg { width: 3.8mm; height: 3.8mm; }
.card.acc-amber .card-icon { background: var(--amber-bg); }
.card.acc-rose .card-icon { background: var(--rose-bg); }
.card.acc-emerald .card-icon { background: var(--emerald-bg); }
.card.acc-indigo .card-icon { background: var(--indigo-bg); }
.card-title { font-size: 8.8pt; font-weight: 700; color: var(--slate-900); margin-bottom: 0.7mm; }
.card-desc { font-size: 7.5pt; line-height: 1.34; color: var(--slate-700); }

.stat-tiles { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2.2mm; }
.stat-tile {
  border-radius: 2.4mm; padding: 2.1mm 2.1mm; text-align: left;
  background: var(--slate-100); border: 1px solid var(--slate-300);
}
.stat-tile .num { font-size: 12pt; font-weight: 800; color: var(--slate-900); line-height: 1; }
.stat-tile .label { font-size: 6.6pt; color: var(--slate-500); margin-top: 0.9mm; line-height: 1.26; font-weight: 600; }
.stat-tile.teal { background: #E7EEFC; border-color: #C1D2F5; }
.stat-tile.amber { background: var(--amber-bg); border-color: #F3D3A6; }
.stat-tile.emerald { background: var(--emerald-bg); border-color: #BEE3CE; }
.stat-tile.indigo { background: var(--indigo-bg); border-color: #D3C4F2; }
.stat-tile.rose { background: var(--rose-bg); border-color: #F0C2CC; }

.pipeline {
  display: flex; align-items: stretch; flex-wrap: wrap; gap: 0mm 0mm;
  background: var(--slate-100); border: 1px solid var(--slate-300); border-radius: 2.6mm; padding: 1.6mm;
}
.pipe-step {
  background: var(--card); border: 1px solid var(--slate-300); border-radius: 2mm;
  padding: 1mm 2mm; font-size: 6.9pt; text-align: center; min-width: 23mm;
}
.pipe-step b { display: block; font-size: 7.4pt; color: var(--slate-900); font-weight: 700; margin-bottom: 0.3mm; }
.pipe-step span { color: var(--slate-500); }
.pipe-arrow { display: flex; align-items: center; justify-content: center; padding: 0 1.4mm; color: var(--teal); font-size: 9pt; font-weight: 700; }
.pipe-step.agent { border-color: var(--amber); background: var(--amber-bg); }
.pipe-step.agent b { color: #5C3406; }

table.kv { width: 100%; border-collapse: collapse; font-size: 7.6pt; }
table.kv th { text-align: left; font-size: 6.9pt; text-transform: uppercase; letter-spacing: 0.5px; color: var(--slate-500); padding: 1.2mm 2mm; border-bottom: 1.5px solid var(--slate-300); }
table.kv td { padding: 1.3mm 2mm; border-bottom: 1px solid var(--slate-100); color: var(--slate-700); vertical-align: top; }
table.kv td.mono, code, .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 7.2pt; color: var(--teal-deep); background: #E7EEFC; padding: 0.4mm 1.4mm; border-radius: 1mm; }
table.kv tr:last-child td { border-bottom: none; }

.codeblock {
  background: var(--ink); color: #D9E6FF; border-radius: 2.4mm; padding: 2.8mm 3.8mm;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 7.6pt; line-height: 1.5;
  white-space: pre-wrap; word-break: break-word;
}
.codeblock .c1 { color: #7A8FBF; }
.codeblock .c2 { color: #7FC4D9; }

ul.tick { list-style: none; padding: 0; margin: 0; }
ul.tick li { position: relative; padding-left: 4.2mm; font-size: 7.2pt; line-height: 1.3; color: var(--slate-700); margin-bottom: 0.6mm; }
ul.tick li::before { content: ""; position: absolute; left: 0; top: 1.5mm; width: 2.1mm; height: 2.1mm; border-radius: 50%; background: var(--teal); }
ul.tick.amber li::before { background: var(--amber); }
ul.tick.rose li::before { background: var(--rose); }

.steps-row { display: flex; gap: 2.6mm; }
.step-pill {
  flex: 1; background: var(--card); border: 1px solid var(--slate-300); border-radius: 2.4mm;
  padding: 2.2mm 2.8mm; font-size: 7.4pt; color: var(--slate-700); display: flex; gap: 1.8mm; align-items: flex-start;
}
.step-pill .n {
  flex-shrink: 0; width: 5mm; height: 5mm; border-radius: 50%; background: var(--teal);
  color: #fff; font-size: 7.6pt; font-weight: 700; display: flex; align-items: center; justify-content: center;
}

.footer-cta {
  margin-top: 2.6mm;
  background: linear-gradient(120deg, var(--ink) 0%, var(--teal-deep) 100%);
  color: #fff; padding: 2.6mm 14mm; display: flex; justify-content: space-between; align-items: center; gap: 8mm;
}
.footer-cta .ftitle { font-size: 11.5pt; font-weight: 800; margin-bottom: 1mm; }
.footer-cta .fsub { font-size: 7.4pt; color: #C9D6EA; }
.footer-cta .fright { text-align: right; font-size: 7.1pt; color: #AFC0DC; }
.footer-cta .fright b { color: #fff; }
.foot-note { text-align: center; font-size: 6.6pt; color: var(--slate-500); padding: 0.7mm 14mm 0 14mm; }

.two-col-body { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 5mm; align-items: start; }
.small-h { font-size: 8pt; font-weight: 700; color: var(--slate-900); margin: 2.4mm 0 1mm 0; }
p.lead { font-size: 8.4pt; line-height: 1.5; color: var(--slate-700); margin: 0 0 1.6mm 0; }
"""


# ---------------------------------------------------------------------------
# Minimal inline icon set (hand-drawn, license-free geometric line icons)
# ---------------------------------------------------------------------------

def icon(name: str, stroke: str = "#1E3A8A") -> str:
    common = f'fill="none" stroke="{stroke}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
    paths = {
        "compass": f'<svg viewBox="0 0 24 24" {common}><circle cx="12" cy="12" r="9"/><path d="M15.2 8.8l-2 6-6 2 2-6z"/></svg>',
        "search": f'<svg viewBox="0 0 24 24" {common}><circle cx="10.5" cy="10.5" r="6.5"/><line x1="21" y1="21" x2="15.2" y2="15.2"/></svg>',
        "link": f'<svg viewBox="0 0 24 24" {common}><path d="M9 15L15 9"/><path d="M11 6l1.5-1.5a4 4 0 015.7 5.7L16.5 12"/><path d="M13 18l-1.5 1.5a4 4 0 01-5.7-5.7L7.5 12"/></svg>',
        "shield": f'<svg viewBox="0 0 24 24" {common}><path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/></svg>',
        "compare": f'<svg viewBox="0 0 24 24" {common}><path d="M7 4v14"/><path d="M17 6V20"/><path d="M4 8h6"/><path d="M14 16h6"/></svg>',
        "route": f'<svg viewBox="0 0 24 24" {common}><circle cx="5" cy="6" r="2.2"/><circle cx="19" cy="18" r="2.2"/><path d="M5 8.2V13a4 4 0 004 4h4"/></svg>',
        "check": f'<svg viewBox="0 0 24 24" {common}><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/></svg>',
        "folder": f'<svg viewBox="0 0 24 24" {common}><path d="M3 6.5A1.5 1.5 0 014.5 5H9l2 2.5h8A1.5 1.5 0 0120.5 9v9A1.5 1.5 0 0119 19.5H4.5A1.5 1.5 0 013 18z"/></svg>',
        "terminal": f'<svg viewBox="0 0 24 24" {common}><rect x="3" y="4" width="18" height="16" rx="1.6"/><path d="M7 9l3.5 3L7 15"/><path d="M13 15h4"/></svg>',
        "alert": f'<svg viewBox="0 0 24 24" {common}><path d="M12 3.5L21.5 20h-19z"/><line x1="12" y1="9.5" x2="12" y2="14"/><circle cx="12" cy="16.8" r="0.4" fill="{stroke}"/></svg>',
        "users": f'<svg viewBox="0 0 24 24" {common}><circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><circle cx="17.5" cy="9" r="2.4"/><path d="M15.5 14c2.6.3 4.5 2 4.5 5"/></svg>',
        "message": f'<svg viewBox="0 0 24 24" {common}><path d="M4 5.5h16v11H9.5L5 20V16.5H4z"/></svg>',
        "sliders": f'<svg viewBox="0 0 24 24" {common}><line x1="5" y1="5" x2="5" y2="19"/><line x1="12" y1="5" x2="12" y2="19"/><line x1="19" y1="5" x2="19" y2="19"/><circle cx="5" cy="9" r="1.7" fill="{stroke}" stroke="none"/><circle cx="12" cy="15" r="1.7" fill="{stroke}" stroke="none"/><circle cx="19" cy="7" r="1.7" fill="{stroke}" stroke="none"/></svg>',
        "book": f'<svg viewBox="0 0 24 24" {common}><path d="M4 5.5c2-1 5-1 7 0v13c-2-1-5-1-7 0z"/><path d="M20 5.5c-2-1-5-1-7 0v13c2-1 5-1 7 0z"/></svg>',
        "layers": f'<svg viewBox="0 0 24 24" {common}><path d="M12 3.5l8 4.2-8 4.2-8-4.2z"/><path d="M4 12l8 4.2 8-4.2"/><path d="M4 15.8L12 20l8-4.2"/></svg>',
        "cpu": f'<svg viewBox="0 0 24 24" {common}><rect x="6.5" y="6.5" width="11" height="11" rx="1.4"/><rect x="10" y="10" width="4" height="4"/><path d="M9 3.5v3M15 3.5v3M9 17.5v3M15 17.5v3M3.5 9h3M3.5 15h3M17.5 9h3M17.5 15h3"/></svg>',
        "lock": f'<svg viewBox="0 0 24 24" {common}><rect x="5.5" y="10.5" width="13" height="9" rx="1.4"/><path d="M8 10.5V7.5a4 4 0 018 0v3"/></svg>',
        "flag": f'<svg viewBox="0 0 24 24" {common}><path d="M6 3.5v17"/><path d="M6 4.5h11l-2.5 3.5L17 11.5H6"/></svg>',
        "clock": f'<svg viewBox="0 0 24 24" {common}><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>',
    }
    return paths.get(name, paths["check"])


def hero(kicker: str, title: str, tagline: str, desc: str, chips: list[str], meta_lines: list[str]) -> str:
    chip_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    return f"""
<div class="hero">
  <div class="hero-top">
    <div class="brandmark">
      <div class="brand-badge">{icon('compass', '#08152E')}</div>
      <div>
        <div class="brand-name">Career Trajectory Optimizer</div>
        <div class="brand-sub">Deep Agents Career Coach</div>
      </div>
    </div>
    <span class="kicker-pill">{kicker}</span>
  </div>
  <div class="hero-title">{title}</div>
  <div class="hero-tagline">{tagline}</div>
  <div class="hero-desc">{desc}</div>
  <div class="chip-row">{chip_html}</div>
</div>
"""


def footer_cta(title: str, sub: str, right_lines: list[str]) -> str:
    right = "<br/>".join(right_lines)
    return f"""
<div class="footer-cta">
  <div>
    <div class="ftitle">{title}</div>
    <div class="fsub">{sub}</div>
  </div>
  <div class="fright">{right}</div>
</div>
"""


def wrap(body_html: str) -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"/><style>{CSS}</style></head>
<body>{body_html}</body></html>"""


# ---------------------------------------------------------------------------
# 1) FLYER
# ---------------------------------------------------------------------------

def flyer_html() -> str:
    hero_block = hero(
        kicker="Learning Project &middot; Deep Agents",
        title="Know your market position.<br/>Get a roadmap you&rsquo;ll actually follow.",
        tagline="Career Trajectory Optimizer &mdash; AI career coach for Indian tech professionals",
        desc="A Deep Agents system that parses your profile, researches the live Indian tech market, benchmarks "
             "your salary, and scores your risk &mdash; then, if you state a goal, builds a personalized 30-60-90 "
             "day roadmap. One orchestrator plans and delegates to eight specialist subagents; nothing is synced "
             "to a calendar without your approval.",
        chips=["Deep Agents", "8 specialist subagents", "Web-grounded research", "Goal-based roadmaps", "Human-approved actions"],
        meta_lines=["<b>Python 3.12+</b> &middot; LangChain/LangGraph", "<b>OpenAI</b> + LinkUp/Tavily (optional)", "Streamlit UI &middot; Jupyter notebook"],
    )

    sound_familiar = f"""
<div class="section-label"><span class="dot dot-rose"></span>The problem with career decisions</div>
<div class="callout callout-rose">
  Indian tech professionals make career decisions with fragmented, incomplete information. Salary data is
  scattered across AmbitionBox, Levels.fyi, and Glassdoor. GenAI roles are growing roughly 180% year-over-year,
  but few people know it. Nothing correlates your actual profile &mdash; skills, tenure, education tier &mdash;
  against the market and against a stated goal. A generic chatbot will happily invent a plausible-sounding salary
  number or timeline; in a career decision, a confident wrong answer costs you months.
</div>
"""

    cards = [
        ("search", "Reads your whole profile", "profile-analyzer parses a resume upload (PDF/DOCX/TXT) or manual entry into a structured timeline, detecting education tier and flagging job-hopping or long tenure.", "teal"),
        ("link", "Researches live, not stale", "market-researcher is the only subagent with web search (LinkUp primary, Tavily fallback) &mdash; it gathers current data so every other subagent reasons from the same grounded brief.", "teal"),
        ("shield", "Never invents a number", "Every salary range and risk score traces back to the grounding file or the researcher&rsquo;s findings &mdash; deterministic validators catch missing or out-of-range values before they reach you.", "rose"),
        ("compare", "Explains your gap", "career-recommender applies goal-specific logic &mdash; target salary, company, role, or GenAI transition &mdash; and states the gap and the levers that close it.", "amber"),
        ("route", "Plans its own steps", "The orchestrator classifies your brief into Profile Analysis Mode or Career Aspiration Mode and delegates accordingly, running independent subagents concurrently to cut wall-clock time.", "indigo"),
        ("check", "Reviewed before you see it", "A dedicated critic subagent checks grounding accuracy, methodology compliance, and internal consistency across every file before the run completes.", "emerald"),
    ]
    colors = {"teal": "#1E3A8A", "rose": "#BE123C", "amber": "#B45309", "indigo": "#6D28D9", "emerald": "#15803D"}
    cards_html = "".join(
        f"""<div class="card acc-{acc}"><div class="card-icon">{icon(ic, colors[acc])}</div>
        <div class="card-title">{t}</div><div class="card-desc">{d}</div></div>"""
        for ic, t, d, acc in cards
    )

    proof = """
<div class="section-label"><span class="dot dot-emerald"></span>What&rsquo;s actually under the hood</div>
<div class="stat-tiles">
  <div class="stat-tile teal"><div class="num">8</div><div class="label">specialist subagents, one orchestrator</div></div>
  <div class="stat-tile indigo"><div class="num">2</div><div class="label">modes: Profile Analysis &amp; Career Aspiration</div></div>
  <div class="stat-tile amber"><div class="num">5</div><div class="label">risk axes scored: salary, skill, security, burnout, growth</div></div>
  <div class="stat-tile emerald"><div class="num">30-60-90</div><div class="label">day roadmap for every stated career goal</div></div>
  <div class="stat-tile rose"><div class="num">&le;60s</div><div class="label">bounded LLM call timeout &mdash; no silent multi-minute stalls</div></div>
</div>
"""

    great_for = [
        ("users", "Working engineers", "See exactly where your current pay and skills sit against the market before you ask for a raise or start interviewing."),
        ("flag", "Job switchers with a goal", "State a target salary, company, or role and get a gap analysis plus a concrete 30-60-90 day plan."),
        ("layers", "GenAI upskillers", "Understand the skill premium and the shortest realistic path to a GenAI-focused role."),
        ("compass", "Career coaches &amp; mentors", "Use the grounded dashboard as a structured starting point for a coaching conversation, not a black-box score."),
    ]
    great_for_html = "".join(
        f"""<div class="card"><div class="card-icon">{icon(ic)}</div><div class="card-title">{t}</div><div class="card-desc">{d}</div></div>"""
        for ic, t, d in great_for
    )

    guided = """
<div class="callout" style="background:linear-gradient(120deg,#0A1220,#1E3A8A);color:#fff;border-left:none;border-radius:3mm;">
  <b style="color:#fff;">Config-driven setup, not a rewrite.</b>
  <span style="color:#DCE7F7;">Swap the model, add LinkUp/Tavily keys, or point the backend at a different store
  entirely through <span class="mono" style="background:rgba(255,255,255,0.18);color:#fff;">.env</span> &mdash;
  the subagent prompts and orchestration logic never change.</span>
</div>
"""

    body = f"""
<div class="page">
  {hero_block}
  <div class="body-wrap">
    {sound_familiar}
    <div class="section-label"><span class="dot dot-teal"></span>Why it&rsquo;s built this way</div>
    <div class="grid-3">{cards_html}</div>
    {proof}
    <div class="section-label"><span class="dot dot-indigo"></span>Great for</div>
    <div class="grid-4">{great_for_html}</div>
    {guided}
  </div>
  {footer_cta(
      "Get your market position in minutes.",
      "Open source &middot; learning project &middot; OpenAI + LinkUp/Tavily &middot; runs on your own machine with Streamlit or Jupyter.",
      ["<b>1.</b> uv sync", "<b>2.</b> streamlit run app.py", "<b>3.</b> Upload your resume"],
  )}
  <div class="foot-note">Career Trajectory Optimizer &middot; Deep Agents multi-agent career coach for Indian tech professionals &middot; built with Python, LangChain, LangGraph &amp; Streamlit</div>
</div>
"""
    return wrap(body)


# ---------------------------------------------------------------------------
# 2) SETUP GUIDE
# ---------------------------------------------------------------------------

def setup_guide_html() -> str:
    hero_block = hero(
        kicker="Setup Guide &middot; v-current",
        title="Setup Guide",
        tagline="Local installation, credentials, and running the agent",
        desc="Everything needed to run Career Trajectory Optimizer end to end: environment setup, provider "
             "credentials, the notebook walkthrough, and the Streamlit UI.",
        chips=["Python 3.12+", "uv", "OpenAI required", "LinkUp/Tavily optional", "~10 min"],
        meta_lines=["<b>Notebook</b> career_optimizer_deep_agent.ipynb", "<b>UI</b> app.py (Streamlit)", "<b>Shared logic</b> agent_core.py"],
    )

    prereqs = [
        ("terminal", "Python 3.12+", "A working interpreter; the project ships a pyproject.toml managed by uv."),
        ("sliders", "uv", "Handles the virtual environment and locked dependency installs via uv sync."),
        ("lock", "OpenAI API key", "Required &mdash; the orchestrator and every subagent call this model."),
        ("search", "LinkUp or Tavily key (optional)", "Enables market-researcher&rsquo;s live web search; omit both to run grounding-only."),
    ]
    prereqs_html = "".join(
        f"""<div class="card"><div class="card-icon">{icon(ic)}</div><div class="card-title">{t}</div><div class="card-desc">{d}</div></div>"""
        for ic, t, d in prereqs
    )

    clone_code = """<span class="c1"># 1. Enter the project</span>
<span class="c2">cd</span> careertrajectoryoptimizer

<span class="c1"># 2. Install dependencies (creates .venv)</span>
uv sync

<span class="c1"># 3. Create your local environment file</span>
cp .env.example .env"""

    env_table = """
<table class="kv">
  <tr><th>Variable</th><th>Purpose</th><th>Example</th></tr>
  <tr><td class="mono">OPENAI_API_KEY</td><td>Required &mdash; powers the orchestrator and all subagents</td><td class="mono">sk-proj-...</td></tr>
  <tr><td class="mono">LINKUP_API_KEY</td><td>Primary web-search provider for market-researcher</td><td class="mono">your-linkup-key</td></tr>
  <tr><td class="mono">TAVILY_API_KEY</td><td>Fallback web-search provider if LinkUp is not set</td><td class="mono">your-tavily-key</td></tr>
  <tr><td class="mono">CAREER_AGENT_MODEL</td><td>Overrides the default model</td><td class="mono">gpt-5-mini</td></tr>
  <tr><td class="mono">LANGSMITH_API_KEY</td><td>Optional nested trace tree tracing</td><td class="mono">lsv2_pt_...</td></tr>
</table>
"""

    run_code = """<span class="c1"># From the project root</span>
uv run streamlit run app.py

<span class="c1"># Open in a browser</span>
<span class="c2">http://localhost:8501</span>"""

    notebook_code = """<span class="c1"># In VS Code / Jupyter, select the project's .venv as the kernel</span>
career_optimizer_deep_agent.ipynb

<span class="c1"># Run the cells top to bottom</span>"""

    subagents_table = """
<table class="kv">
  <tr><th>Subagent</th><th>Role</th><th>Tools</th></tr>
  <tr><td class="mono">profile-analyzer</td><td>Parses profile/resume into a structured timeline</td><td>filesystem only</td></tr>
  <tr><td class="mono">market-researcher</td><td>Gathers live Indian tech market data</td><td class="mono">web_search (LinkUp/Tavily)</td></tr>
  <tr><td class="mono">salary-intelligence</td><td>Benchmarks pay vs. market</td><td>reads research brief</td></tr>
  <tr><td class="mono">market-tracker</td><td>Tracks skill demand &amp; trends</td><td>reads research brief</td></tr>
  <tr><td class="mono">risk-scorer</td><td>Scores 5-axis risk dashboard</td><td class="mono">risk_dashboard_validator</td></tr>
  <tr><td class="mono">career-recommender</td><td>Goal-based gap analysis (Aspiration Mode)</td><td>reads all analysis</td></tr>
  <tr><td class="mono">roadmap-planner</td><td>Builds the 30-60-90 day roadmap</td><td class="mono">roadmap_validator</td></tr>
  <tr><td class="mono">critic</td><td>Reviews grounding, methodology, consistency</td><td>both validators</td></tr>
</table>
"""

    troubleshoot = [
        ("alert", "OPENAI_API_KEY missing", "The Streamlit sidebar shows a red status and blocks the agent from building; add it to <span class=\"mono\">.env</span> and refresh.", "rose"),
        ("clock", "A run takes 5+ minutes", "Expected &mdash; 6 to 9 subagents each run their own multi-turn loop. Career Aspiration Mode and the calendar-sync HITL gate add more time.", "amber"),
        ("alert", "A single call stalls for minutes", "Likely a per-minute rate limit; the model is bounded to <span class=\"mono\">max_retries=2, timeout=60s</span> so it fails fast and visibly instead.", "rose"),
        ("folder", "Resume text looks incomplete", "Many resumes lay out skills/experience in tables &mdash; the extractor walks the whole document (paragraphs + nested tables) to avoid missing them.", "teal"),
    ]
    troubleshoot_html = "".join(
        f"""<div class="card acc-{acc}"><div class="card-icon">{icon(ic, {'teal':'#1E3A8A','rose':'#BE123C','amber':'#B45309','emerald':'#15803D'}[acc])}</div>
        <div class="card-title">{t}</div><div class="card-desc">{d}</div></div>"""
        for ic, t, d, acc in troubleshoot
    )

    body = f"""
<div class="page">
  {hero_block}
  <div class="body-wrap">
    <div class="section-label"><span class="dot dot-teal"></span>Prerequisites</div>
    <div class="grid-4">{prereqs_html}</div>

    <div class="section-label"><span class="dot dot-teal"></span>1&middot; Clone &amp; install</div>
    <div class="codeblock">{clone_code}</div>

    <div class="section-label"><span class="dot dot-teal"></span>2&middot; Configure credentials</div>
    <p class="lead">Copy <span class="mono">.env.example</span> to <span class="mono">.env</span> and fill in the values below. Only <span class="mono">OPENAI_API_KEY</span> is required.</p>
    {env_table}
  </div>
</div>
<div class="page">
  <div class="body-wrap" style="padding-top:12mm;">
    <div class="section-label"><span class="dot dot-teal"></span>3&middot; Run the app</div>
    <div class="codeblock">{run_code}</div>

    <div class="section-label"><span class="dot dot-indigo"></span>4&middot; Or run the notebook</div>
    <div class="codeblock">{notebook_code}</div>

    <div class="section-label"><span class="dot dot-emerald"></span>5&middot; Subagents at a glance</div>
    {subagents_table}

    <div class="section-label"><span class="dot dot-rose"></span>Troubleshooting</div>
    <div class="grid-2">{troubleshoot_html}</div>
  </div>
  {footer_cta(
      "Ready to run in about 10 minutes.",
      "No infrastructure to stand up &mdash; the store, checkpointer, and backend are all in-process; only your API keys are external.",
      ["<b>1.</b> uv sync", "<b>2.</b> Configure .env", "<b>3.</b> streamlit run", "<b>4.</b> Upload a resume"],
  )}
  <div class="foot-note">Career Trajectory Optimizer &middot; Setup Guide &middot; local installation and runtime configuration</div>
</div>
"""
    return wrap(body)


# ---------------------------------------------------------------------------
# 3) TECHNICAL BRIEF
# ---------------------------------------------------------------------------

def technical_brief_html() -> str:
    hero_block = hero(
        kicker="Technical Product Brief &middot; v-current",
        title="Career Trajectory Optimizer",
        tagline="A Deep Agents multi-agent career coach for Indian tech professionals",
        desc="An orchestrator plans, detects intent, and delegates to eight specialist subagents &mdash; profile "
             "parsing, live market research, salary benchmarking, market tracking, risk scoring, goal-based "
             "recommendation, roadmap planning, and critique &mdash; sharing state through a composite "
             "filesystem + store backend, with a human-in-the-loop gate before any simulated calendar sync.",
        chips=["Python 3.12+", "LangChain/LangGraph", "Deep Agents", "OpenAI", "Streamlit"],
        meta_lines=["<b>Model</b> gpt-5-mini (configurable)", "<b>Search</b> LinkUp &rarr; Tavily fallback", "<b>Memory</b> InMemoryStore (swap for Postgres)"],
    )

    what_it_is = """
<div class="callout callout-teal">
  <b>What it is.</b> A Deep Agents application: one orchestrator LLM plans with <span class="mono">write_todos</span>,
  detects whether the user stated a career goal, and delegates isolated, stateless subagent runs via the
  <span class="mono">task</span> tool. Findings pass between subagents through a shared virtual filesystem
  (<span class="mono">CompositeBackend</span>: disk for /profile /research /analysis /roadmap, a Store for
  /memories). A checkpointer enables a pause-and-resume human approval gate before the (simulated) calendar-sync
  action.
</div>
"""

    pipe1 = """
<div class="pipeline">
  <div class="pipe-step"><b>Profile</b><span>resume upload or manual entry</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step"><b>profile-analyzer</b><span>structured timeline</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step"><b>market-researcher</b><span>web_search, LinkUp/Tavily</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step"><b>salary + market</b><span>concurrent delegation</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step"><b>risk-scorer</b><span>5-axis dashboard</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step"><b>critic</b><span>grounding + consistency review</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step"><b>memory</b><span>/memories/career_progress.md</span></div>
</div>
"""

    pipe2 = """
<div class="pipeline">
  <div class="pipe-step agent"><b>Intent detection</b><span>goal stated in brief?</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step agent"><b>career-recommender</b><span>goal-based gap analysis</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step agent"><b>roadmap-planner</b><span>30-60-90 day plan</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step agent"><b>sync_to_calendar</b><span>one call per checkpoint</span></div><div class="pipe-arrow">&rarr;</div>
  <div class="pipe-step agent"><b>HITL gate</b><span>human approve / reject</span></div>
</div>
"""

    col_a = """
<div class="card">
  <div class="card-title" style="font-size:10pt;margin-bottom:1.2mm;">Subagents &amp; division of labour</div>
  <ul class="tick">
    <li><b>Eight specialists, one orchestrator.</b> profile-analyzer, market-researcher, salary-intelligence, market-tracker, risk-scorer, career-recommender, roadmap-planner, critic &mdash; each with its own prompt, tools, and skills.</li>
    <li><b>Single web-search owner.</b> Only market-researcher holds the web_search tool (LinkUp primary, Tavily fallback); every other subagent reads /research/market_brief.md instead of searching independently.</li>
    <li><b>Concurrent delegation.</b> salary-intelligence and market-tracker are delegated in the same orchestrator step &mdash; both are independent of each other, so they execute together instead of sequentially.</li>
    <li><b>Skills as progressive disclosure.</b> salary-benchmarking and roadmap-planning SKILL.md methodology guides load on demand, keeping the base system prompt lean.</li>
  </ul>
</div>
"""

    col_b = """
<div class="card acc-amber">
  <div class="card-title" style="font-size:10pt;margin-bottom:1.2mm;">Backends &amp; persistence</div>
  <ul class="tick amber">
    <li><b>CompositeBackend routing.</b> /profile, /research, /analysis, /roadmap resolve to real files on disk (FilesystemBackend); /memories/* resolves to a Store instead.</li>
    <li><b>Cross-session memory.</b> career_progress.md persists in an InMemoryStore (swap for a Postgres-backed store in production) so a new thread can recall prior findings.</li>
    <li><b>Checkpointer.</b> A MemorySaver holds per-thread state &mdash; required for the human-in-the-loop interrupt to pause and later resume mid-run.</li>
    <li><b>Stateless subagents.</b> Each task call is a fresh run with no memory of prior subagent turns &mdash; instructions must be self-contained.</li>
  </ul>
</div>
"""

    col_c = """
<div class="card acc-indigo">
  <div class="card-title" style="font-size:10pt;margin-bottom:1.2mm;">Validation, HITL &amp; safety</div>
  <ul class="tick">
    <li><b>Deterministic validators.</b> roadmap_validator and risk_dashboard_validator check required sections and 0-10 score ranges in code, not by asking the model to self-report.</li>
    <li><b>Human-in-the-loop gate.</b> <span class="mono">interrupt_on={"sync_to_calendar": True}</span> pauses before every simulated calendar sync; the run resumes only after an explicit approve/reject decision.</li>
    <li><b>Critic pass.</b> A dedicated critic subagent checks grounding accuracy, skill-methodology compliance, and cross-file consistency before the run is considered complete.</li>
    <li><b>Placeholder-key guard.</b> Unfilled .env.example values are explicitly detected and treated as &ldquo;not configured&rdquo;, not as a live credential.</li>
  </ul>
</div>
"""

    col_d = """
<div class="card acc-emerald">
  <div class="card-title" style="font-size:10pt;margin-bottom:1.2mm;">Resilience &amp; observability</div>
  <ul class="tick" style="--tick-color:var(--emerald);">
    <li><b>Bounded retries.</b> The chat model is constructed explicitly with max_retries=2, timeout=60s &mdash; a rate-limit hit fails fast and visibly instead of silently backing off for minutes.</li>
    <li><b>Streamed live progress.</b> The Streamlit UI streams <span class="mono">agent.stream(..., stream_mode="values")</span> into a status panel instead of a static spinner, surfacing each delegation as it happens.</li>
    <li><b>Structured trace.</b> build_trace_entries() parses raw messages into a labeled, sequential trace &mdash; planning, delegation, subagent result, final answer &mdash; instead of a flat role/content dump.</li>
    <li><b>Optional LangSmith tracing.</b> Setting LANGSMITH_API_KEY uploads a full nested trace tree: orchestrator, each task child span, and the subagent&rsquo;s internal LLM + tool calls.</li>
  </ul>
</div>
"""

    stat_strip = """
<div class="stat-tiles" style="grid-template-columns:repeat(6,1fr);">
  <div class="stat-tile teal"><div class="num">8</div><div class="label">specialist subagents</div></div>
  <div class="stat-tile indigo"><div class="num">2</div><div class="label">operating modes</div></div>
  <div class="stat-tile amber"><div class="num">5</div><div class="label">risk axes scored</div></div>
  <div class="stat-tile"><div class="num">2&times;</div><div class="label">search providers, primary + fallback</div></div>
  <div class="stat-tile rose"><div class="num">&le;60s</div><div class="label">bounded LLM call timeout</div></div>
  <div class="stat-tile emerald"><div class="num">1</div><div class="label">HITL gate before any simulated external action</div></div>
</div>
"""

    body = f"""
<div class="page">
  {hero_block}
  <div class="body-wrap">
    {what_it_is}
    <div class="section-label"><span class="dot dot-teal"></span>Shared pipeline (every run)</div>
    {pipe1}
    <div class="section-label"><span class="dot dot-amber"></span>Career aspiration mode only</div>
    {pipe2}
    <div class="grid-2" style="margin-top:1.8mm;">{col_a}{col_b}</div>
    <div class="grid-2" style="margin-top:1.4mm;">{col_c}{col_d}</div>
    <div class="section-label" style="margin-top:2mm;"><span class="dot dot-teal"></span>At a glance</div>
    {stat_strip}
  </div>
  <div class="foot-note" style="margin-top:8mm;">Career Trajectory Optimizer &mdash; Technical Product Brief &middot; Deep Agents multi-agent career coach &middot; Python &middot; LangChain &middot; LangGraph &middot; OpenAI</div>
</div>
"""
    return wrap(body)


# ---------------------------------------------------------------------------
# 4) USER GUIDE
# ---------------------------------------------------------------------------

def user_guide_html() -> str:
    hero_block = hero(
        kicker="User Guide",
        title="Using Career Trajectory Optimizer",
        tagline="Understand your market position, or get a roadmap to a stated goal",
        desc="A practical walkthrough: what to upload, how Profile Analysis Mode differs from Career Aspiration "
             "Mode, how to read the risk dashboard and roadmap, and how the calendar-sync approval step works.",
        chips=["Streamlit UI", "Resume upload", "Goal-based roadmap", "Human-approved sync"],
        meta_lines=["<b>App</b> app.py (Streamlit)", "<b>Notebook</b> career_optimizer_deep_agent.ipynb", "<b>Modes</b> Profile Analysis &middot; Career Aspiration"],
    )

    who_for = [
        ("users", "Working engineers", "See your current market position &mdash; salary range, skill demand, and readiness &mdash; before a performance review or job search."),
        ("flag", "Job switchers with a goal", "State a target salary, company, or role and get a gap analysis with a concrete 30-60-90 day plan."),
        ("layers", "GenAI upskillers", "Understand the GenAI skill premium and the realistic timeline to transition into a GenAI-focused role."),
        ("compare", "Coaches &amp; mentors", "Use the grounded dashboard as a structured, citation-backed starting point for a coaching conversation."),
    ]
    who_html = "".join(
        f"""<div class="card"><div class="card-icon">{icon(ic)}</div><div class="card-title">{t}</div><div class="card-desc">{d}</div></div>"""
        for ic, t, d in who_for
    )

    steps_html = """
<div class="steps-row">
  <div class="step-pill"><div class="n">1</div><div>Upload your resume (PDF, DOCX, or TXT) &mdash; the extracted text appears in an editable box so you can review or add details before running.</div></div>
  <div class="step-pill"><div class="n">2</div><div>State a career goal for a full roadmap, or leave it blank for a market-position analysis only.</div></div>
  <div class="step-pill"><div class="n">3</div><div>Click Run analysis and watch the live status panel as the orchestrator delegates to each subagent in sequence.</div></div>
</div>
"""

    examples_table = """
<table class="kv">
  <tr><th>Goal type</th><th>Example</th></tr>
  <tr><td>Profile Analysis</td><td>&ldquo;No goal &mdash; 4 years as a Backend Engineer, Python/Django/AWS, tier-2 college. Just show me where I stand.&rdquo;</td></tr>
  <tr><td>Salary goal</td><td>&ldquo;I want to earn &#8377;100L within 2 years.&rdquo;</td></tr>
  <tr><td>Company goal</td><td>&ldquo;I want to transform into an AI FDE engineer at FAANG.&rdquo;</td></tr>
  <tr><td>Role goal</td><td>&ldquo;I want to become a Tech Lead within my current company.&rdquo;</td></tr>
  <tr><td>GenAI transition</td><td>&ldquo;I want to become a GenAI Engineer within 6 months.&rdquo;</td></tr>
  <tr><td>Relocation goal</td><td>&ldquo;I want to work remotely for a US company.&rdquo;</td></tr>
</table>
"""

    reading = """
<div class="grid-2">
  <div class="card">
    <div class="card-icon">""" + icon("check") + """</div>
    <div class="card-title">Risk dashboard</div>
    <div class="card-desc">Five scores (0-10 each): salary, skill, security, burnout, growth risk &mdash; validated in code, not self-reported by the model.</div>
  </div>
  <div class="card acc-rose">
    <div class="card-icon">""" + icon("alert", "#BE123C") + """</div>
    <div class="card-title">Human approval gate</div>
    <div class="card-desc">Before any calendar-sync action, the run pauses and shows exactly what it wants to do. Approve or reject &mdash; nothing is synced without your decision.</div>
  </div>
</div>
"""

    limits = """
<div class="callout callout-amber">
  <b>What it won&rsquo;t do.</b> Without a LinkUp or Tavily key it falls back to grounding-only market facts &mdash;
  still honest, but not live. The calendar sync is <b>simulated</b>; nothing is ever actually written to a real
  calendar. Salary and timeline estimates are grounded projections, not guarantees &mdash; always sanity-check a
  major decision against current, specific offers.
</div>
"""

    best_practices = """
<ul class="tick">
  <li>Upload a complete resume rather than a short summary &mdash; profile-analyzer works from whatever text it receives.</li>
  <li>State a specific, time-bound goal (&ldquo;&#8377;100L in 2 years&rdquo;) rather than a vague one (&ldquo;more money&rdquo;) so the recommender can compute a real gap.</li>
  <li>Review the extracted resume text box before running &mdash; fix any parsing gaps first.</li>
  <li>Treat a long run time (several minutes) as normal, not a hang &mdash; the live status panel shows which subagent is currently working.</li>
</ul>
"""

    body = f"""
<div class="page">
  {hero_block}
  <div class="body-wrap">
    <div class="section-label"><span class="dot dot-teal"></span>Who this is for</div>
    <div class="grid-4">{who_html}</div>

    <div class="section-label"><span class="dot dot-teal"></span>Getting started</div>
    {steps_html}

    <div class="section-label"><span class="dot dot-indigo"></span>Example goals</div>
    {examples_table}

    <div class="section-label"><span class="dot dot-teal"></span>Reading a result</div>
    {reading}

    <div class="section-label"><span class="dot dot-amber"></span>Limits, honestly stated</div>
    {limits}

    <div class="section-label"><span class="dot dot-emerald"></span>Best practices</div>
    {best_practices}
  </div>
  {footer_cta(
      "Get a grounded answer, not a guess.",
      "Every number traces back to your profile or the market-researcher's findings &mdash; reviewed by a dedicated critic before you see it.",
      ["<b>Streamlit</b> UI", "<b>localhost:8501</b>", "Grounded &middot; Reviewed &middot; Yours"],
  )}
  <div class="foot-note">Career Trajectory Optimizer &middot; User Guide &middot; using the AI career coach</div>
</div>
"""
    return wrap(body)


# ---------------------------------------------------------------------------
# Build + convert
# ---------------------------------------------------------------------------

DOCS: list[tuple[str, str]] = [
    ("01_flyer", flyer_html()),
    ("02_setup_guide", setup_guide_html()),
    ("03_technical_brief", technical_brief_html()),
    ("04_user_guide", user_guide_html()),
]


def find_chrome() -> str:
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    raise RuntimeError("No Chrome/Chromium binary found for HTML->PDF conversion.")


def render_pdf(chrome_bin: str, html_path: Path, pdf_path: Path) -> None:
    subprocess.run(
        [
            chrome_bin,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={pdf_path}",
            str(html_path),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    chrome_bin = find_chrome()
    for stem, html in DOCS:
        html_path = HTML_DIR / f"{stem}.html"
        pdf_path = PDF_DIR / f"{stem}.pdf"
        html_path.write_text(html, encoding="utf-8")
        render_pdf(chrome_bin, html_path, pdf_path)
        print(f"- {pdf_path.relative_to(DOCS_DIR.parent)}")

    for stale in PDF_DIR.glob("*.pdf"):
        if stale.stem not in {stem for stem, _ in DOCS}:
            stale.unlink()

    print(f"\nGenerated {len(DOCS)} PDFs in {PDF_DIR}")


if __name__ == "__main__":
    main()
