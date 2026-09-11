"""Streamlit UI for the Career Trajectory Optimizer Deep Agent.

Run with:
    uv run streamlit run app.py

This wraps the exact agent built in `career_optimizer_deep_agent.ipynb` (via
`agent_core.py`) with an interactive front end: profile/goal input, live shared-state
file inspection, the calendar-sync human-approval gate, and a cross-session memory check.

Credentials are read from `.env` (see `.env.example`) — not entered in the UI.
"""
import os
import uuid

import streamlit as st
from dotenv import load_dotenv
from langgraph.types import Command

from agent_core import (
    PROJECT_DIR,
    RESUME_FILE_TYPES,
    _is_real_key,
    build_agent,
    extract_resume_text,
    invoke_with_retry,
    pending_requests,
    print_trace_to_console,
    render_text_pdf,
    run_agent_with_retry,
)

ENV_PATH = PROJECT_DIR / ".env"
load_dotenv(ENV_PATH)

st.set_page_config(page_title="Career Trajectory Optimizer", page_icon="\U0001F9ED", layout="wide")
st.title("Career Trajectory Optimizer")
st.caption("AI career coach for Indian tech professionals — Deep Agents multi-agent demo")

MODEL = os.environ.get("CAREER_AGENT_MODEL", "gpt-5-mini")

# --- Sidebar: session controls (credentials come from .env, not the UI) ----
with st.sidebar:
    st.header("Setup")
    has_openai = _is_real_key(os.environ.get("OPENAI_API_KEY", ""))
    has_linkup = _is_real_key(os.environ.get("LINKUP_API_KEY", ""))
    has_tavily = _is_real_key(os.environ.get("TAVILY_API_KEY", ""))

    st.write("OPENAI_API_KEY:", "✅ found" if has_openai else "❌ missing")
    if has_linkup:
        st.write("Web search:", "✅ LinkUp (primary)")
    elif has_tavily:
        st.write("Web search:", "✅ Tavily (fallback)")
    else:
        st.write("Web search:", "⚠️ optional, not set")

    if not has_openai:
        st.error(f"Add OPENAI_API_KEY to:\n\n`{ENV_PATH}`\n\nthen restart the app.")

    st.divider()
    if st.button("New session (new thread)"):
        st.session_state.pop("thread_id", None)
        st.session_state.pop("result", None)

if has_openai and "agent" not in st.session_state:
    with st.spinner("Assembling deep agent..."):
        agent, backend, store, checkpointer = build_agent(model=MODEL)
        st.session_state.agent = agent
        st.session_state.backend = backend
        st.session_state.store = store
        st.session_state.checkpointer = checkpointer

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"career-{uuid.uuid4().hex[:8]}"

if "agent" not in st.session_state:
    st.info("Add OPENAI_API_KEY to `.env` and refresh the page to start.")
    st.stop()

agent = st.session_state.agent
config = {"configurable": {"thread_id": st.session_state.thread_id}, "recursion_limit": 60}

# --- Main input form ---------------------------------------------------------
st.subheader("1. Your profile")
uploaded_resume = st.file_uploader("Upload your resume", type=RESUME_FILE_TYPES)

if uploaded_resume is not None and st.session_state.get("_resume_name") != uploaded_resume.name:
    with st.spinner("Parsing resume..."):
        try:
            extracted_text = extract_resume_text(uploaded_resume.name, uploaded_resume.getvalue())
            st.session_state.profile_text = extracted_text
            st.session_state._resume_name = uploaded_resume.name
        except Exception as e:
            st.error(f"Could not parse resume: {e}")

profile_text = st.text_area(
    "Extracted resume text (review or edit before running; you can also type/paste directly here)",
    height=180,
    placeholder=(
        "Upload a resume above, or describe your background here, e.g. \"4 years as a Backend "
        "Engineer at a mid-size product company in Bengaluru, B.Tech from a tier-2 college, "
        "skills in Python, Django, PostgreSQL, AWS.\""
    ),
    key="profile_text",
)

st.subheader("2. Career goal (optional — leave blank for Profile Analysis Mode)")
goal_text = st.text_input(
    "e.g. \"I want to transform into an AI FDE engineer at FAANG\""
)

run_clicked = st.button("Run analysis", type="primary", disabled=not profile_text.strip())

if run_clicked:
    brief = f"Profile: {profile_text.strip()}"
    if goal_text.strip():
        brief += f" Goal: {goal_text.strip()}"
    else:
        brief += " No specific goal yet — just show me where I stand in the market today."

    # This pipeline runs several subagents in sequence (each doing its own multi-turn
    # reasoning), so a single run typically takes a few minutes — stream a brief live
    # status instead of a static spinner so it's clear the run is progressing, not stuck.
    # Detailed logs print to the console only (see print_trace_to_console below).
    # A transient error (e.g. an LLM request timeout) is retried automatically,
    # resuming from the last completed step instead of restarting the whole run.
    with st.status("Starting analysis...", expanded=True) as status:
        try:
            state = run_agent_with_retry(
                agent,
                {"messages": [{"role": "user", "content": brief}]},
                config,
                on_progress=lambda label: status.update(label=label),
            )
            status.update(label="Analysis complete", state="complete")
            st.session_state.result = state
            print_trace_to_console(state["messages"])
        except Exception as e:
            status.update(label="Analysis failed", state="error")
            st.session_state.result = None
            st.error(f"The run failed after retries: {type(e).__name__}: {e}")

# --- Results -----------------------------------------------------------------
result = st.session_state.get("result")
if result:
    st.divider()
    st.subheader("Stage-by-stage results")
    st.caption("A consolidated read of what each subagent produced, in pipeline order. (Detailed logs print to the console.)")
    stage_files = [
        ("Profile", ["profile/timeline.md"]),
        ("Market research", ["research/market_brief.md"]),
        ("Salary intelligence", ["analysis/salary.md"]),
        ("Market trends", ["analysis/market_trends.md"]),
        ("Risk dashboard", ["analysis/risk_dashboard.md"]),
        ("Recommendation", ["analysis/recommendation.md"]),
        ("Roadmap", ["roadmap/plan.md"]),
    ]
    for stage_name, rels in stage_files:
        for rel in rels:
            p = PROJECT_DIR / rel
            if p.exists():
                st.markdown(f"**{stage_name}**")
                st.markdown(p.read_text())
                st.markdown("---")

    with st.expander("Todos"):
        for t in result.get("todos", []):
            st.checkbox(t.get("content", ""), value=(t.get("status") == "completed"), disabled=True)

    # --- HITL approval gate ---------------------------------------------------
    reqs = pending_requests(result)
    if reqs:
        st.divider()
        st.subheader("Human approval required — calendar sync")
        for r in reqs:
            st.json(r)
        col1, col2 = st.columns(2)
        if col1.button("Approve all"):
            decisions = [{"type": "approve"} for _ in reqs]
            try:
                with st.spinner("Resuming..."):
                    st.session_state.result = invoke_with_retry(
                        agent, Command(resume={"decisions": decisions}), config,
                    )
                print_trace_to_console(st.session_state.result["messages"])
            except Exception as e:
                st.error(f"Resume failed after retries: {type(e).__name__}: {e}")
            st.rerun()
        if col2.button("Reject all"):
            decisions = [{"type": "reject", "message": "Not approved from the UI."} for _ in reqs]
            try:
                with st.spinner("Resuming..."):
                    st.session_state.result = invoke_with_retry(
                        agent, Command(resume={"decisions": decisions}), config,
                    )
                print_trace_to_console(st.session_state.result["messages"])
            except Exception as e:
                st.error(f"Resume failed after retries: {type(e).__name__}: {e}")
            st.rerun()
    else:
        synced = [
            tc["args"].get("task_description")
            for m in result["messages"]
            for tc in (getattr(m, "tool_calls", None) or [])
            if tc["name"] == "sync_to_calendar"
        ]
        if synced:
            st.success(f"Synced checkpoints: {', '.join(synced)}")

    # --- Final recommendation ---------------------------------------------
    if not reqs:
        st.divider()
        st.subheader("Final Recommendation")
        final_text = result["messages"][-1].content or "(no final response)"
        st.markdown(final_text)

        pdf_bytes = render_text_pdf(
            title="Career Trajectory Optimizer \u2014 Recommendation",
            subtitle=f"Session: {st.session_state.thread_id}",
            body_text=final_text,
        )
        if pdf_bytes:
            st.download_button(
                "Download recommendation as PDF",
                data=pdf_bytes,
                file_name="career_recommendation.pdf",
                mime="application/pdf",
            )
        else:
            st.caption("PDF download unavailable \u2014 no Chrome/Chromium binary found on this machine.")

# --- Memory check --------------------------------------------------------------
st.divider()
st.subheader("3. Check remembered progress (new thread)")
if st.button("Ask a fresh session to recall my progress"):
    memory_config = {
        "configurable": {"thread_id": f"{st.session_state.thread_id}-checkin"},
        "recursion_limit": 20,
    }
    try:
        with st.spinner("Reading /memories/career_progress.md..."):
            memory_result = invoke_with_retry(
                agent,
                {"messages": [{"role": "user",
                               "content": "Read /memories/career_progress.md and summarise where we left off in one line."}]},
                memory_config,
            )
        st.info(memory_result["messages"][-1].content)
    except Exception as e:
        st.error(f"Memory check failed after retries: {type(e).__name__}: {e}")
