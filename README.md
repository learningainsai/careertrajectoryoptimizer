# Career Trajectory Optimizer (India)

A Deep Agents tutorial project — LangChain's batteries-included agent layer on LangGraph —
built to the exact technical pattern of the `Deep Agent` GTM tutorial in this workspace.
The driver is the notebook **`career_optimizer_deep_agent.ipynb`**.

**Use case:** an AI career coach for Indian tech professionals. An orchestrator delegates
to seven specialist subagents to parse a profile, benchmark salary, track market demand,
score risk, and — when the user states a career goal — build a personalized roadmap with
a 30-60-90 day plan. Analysis-only — nothing is ever actually synced to a calendar.

## Setup (uv)

```bash
uv sync                       # install dependencies into .venv
cp .env.example .env          # then add your OPENAI_API_KEY (Tavily optional)
```

Open `career_optimizer_deep_agent.ipynb` and select the project's `.venv` as the kernel,
then run the cells top to bottom. (If keys aren't in `.env`, the notebook prompts for them.)

## Interactive UI

A Streamlit front end wraps the same agent (via `agent_core.py`) for click-through use
instead of running the notebook cell by cell:

```bash
uv run streamlit run app.py
```

Enter your API key(s) in the sidebar, click **Build / rebuild agent**, then submit a
profile (and optional goal) to run the analysis, inspect shared-state files, approve the
calendar-sync human-in-the-loop gate, and check persisted cross-session memory.

## Layout

| Path | What it is |
|---|---|
| `career_optimizer_deep_agent.ipynb` | The tutorial — run/explain cell by cell |
| `agent_core.py` | Shared agent-building logic used by `app.py` |
| `app.py` | Streamlit UI on top of the same Deep Agent |
| `grounding/india_market_context.md` | Indian tech market facts the agent is grounded in |
| `skills/salary-benchmarking/SKILL.md` | Salary benchmarking methodology (loaded on demand) |
| `skills/roadmap-planning/SKILL.md` | 30-60-90 roadmap methodology (loaded on demand) |
| `profile/`, `analysis/`, `roadmap/` | Created at runtime by the agent (gitignored) |

## Concepts demonstrated

Planning (`write_todos`) · subagent delegation (`task`) with isolated context · shared
filesystem state · skills (progressive disclosure) · cross-session memory via a `Store` ·
human-in-the-loop approval · `recursion_limit` as the runaway-loop backstop · intent-based
branching between Profile Analysis Mode and Career Aspiration Mode.
