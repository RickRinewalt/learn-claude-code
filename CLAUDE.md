# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"Learn Claude Code" is an educational project that teaches agent harness engineering through 12 progressive Python implementations (`s01`–`s12`) and an interactive Next.js web app. The core thesis: **the model is the agent; the code is the harness** (tools, context, permissions).

Live site: https://learn.shareai.run

## Build & Dev Commands

### Web app (Next.js, in `web/`)
```bash
cd web
npm ci                    # install dependencies
npm run dev               # dev server (runs extract first via predev hook)
npm run build             # production build (static export, runs extract first)
npx tsc --noEmit          # type check
npm run extract           # regenerate web/src/data/generated/ from agents/ and docs/
```

### Python agents (in `agents/`)
```bash
pip install -r requirements.txt       # or: pip install 'anthropic[bedrock]' python-dotenv
cp .env.example .env                  # then configure PROVIDER and MODEL_ID

# AWS Bedrock (default): set AWS_PROFILE and AWS_REGION
PROVIDER=bedrock AWS_PROFILE=my-profile MODEL_ID=us.anthropic.claude-sonnet-4-6-v1:0 python agents/s01_agent_loop.py

# Direct Anthropic API:
PROVIDER=anthropic ANTHROPIC_API_KEY=sk-ant-xxx MODEL_ID=claude-sonnet-4-6 python agents/s01_agent_loop.py
```

### CI checks (what PR checks run)
- **CI workflow**: `cd web && npx tsc --noEmit && npm run build`
- **Test workflow**: `python tests/test_unit.py` + per-session integration tests (require API key secrets)

## Architecture

### Two-part structure
1. **`agents/`** — 12 Python files (`s01_agent_loop.py` through `s12_worktree_task_isolation.py`) plus `s_full.py` (capstone). Each file is self-contained and progressively adds one mechanism to the agent harness.
2. **`web/`** — Next.js 16 static-export app (React 19, Tailwind v4, TypeScript). Renders the learning content with interactive visualizations and an agent loop simulator.

### Content pipeline
`web/scripts/extract-content.ts` parses the Python source files and markdown docs into structured JSON:
- **Input**: `agents/*.py` + `docs/{en,zh,ja}/*.md`
- **Output**: `web/src/data/generated/versions.json` and `web/src/data/generated/docs.json`
- Runs automatically before `dev` and `build` via npm `predev`/`prebuild` hooks

### Web app routing
Uses Next.js App Router with `[locale]` and `[version]` dynamic segments:
- `app/[locale]/page.tsx` — landing/home
- `app/[locale]/(learn)/[version]/page.tsx` — main session view (source, docs, simulator, visualization)
- `app/[locale]/(learn)/[version]/diff/page.tsx` — diff between consecutive sessions
- `app/[locale]/(learn)/compare/` — side-by-side comparison
- `app/[locale]/(learn)/layers/` — architectural layer view
- `app/[locale]/(learn)/timeline/` — timeline view

Supported locales: `en`, `zh`, `ja`. i18n via `web/src/i18n/messages/{locale}.json` and a custom `I18nProvider`.

### Key data structures
- **`web/src/lib/constants.ts`** — `VERSION_ORDER`, `VERSION_META`, `LAYERS` define the 12 sessions, their metadata, and which architectural layer each belongs to (tools, planning, memory, concurrency, collaboration)
- **`web/src/types/agent-data.ts`** — TypeScript types for `AgentVersion`, `VersionDiff`, `Scenario`, `SimStep`, flow diagrams
- **`web/src/data/scenarios/s*.json`** — step-by-step simulator data for each session
- **`web/src/data/annotations/s*.json`** — code annotations for each session
- **`web/src/components/visualizations/s*.tsx`** — per-session interactive visualizations (stepped animations via `useSteppedVisualization` hook)

### Python agent pattern
Each `agents/s*.py` follows a consistent structure:
- Module docstring with ASCII architecture diagram
- Client import from shared `agents/client.py` (supports Bedrock and direct Anthropic API via `PROVIDER` env var)
- Tool definitions as dicts with `input_schema`
- Tool dispatch: `TOOL_HANDLERS = {"bash": run_bash, ...}`
- Agent loop: `while stop_reason == "tool_use"` → call LLM → execute tools → append results
- REPL for interactive use

### Environment
The `PROVIDER` env var controls the backend: `bedrock` (default, uses `AnthropicBedrock` with boto3 credential chain) or `anthropic` (uses `Anthropic` with `ANTHROPIC_API_KEY`). The `.env.example` documents both modes plus compatible third-party providers (MiniMax, GLM, Kimi, DeepSeek) via `ANTHROPIC_BASE_URL`.

## Session progression (what each adds)
| Session | Adds |
|---------|------|
| s01 | Agent loop + bash tool |
| s02 | Multi-tool dispatch map |
| s03 | TodoWrite for planning |
| s04 | Subagent spawning with isolated context |
| s05 | On-demand skill/knowledge loading |
| s06 | Three-layer context compression |
| s07 | File-based task graph with dependencies |
| s08 | Background execution + notification queue |
| s09 | Teammate spawning + async mailboxes |
| s10 | Request-response team protocols |
| s11 | Autonomous task board claiming |
| s12 | Git worktree isolation per task |
