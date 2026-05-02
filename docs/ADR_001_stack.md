# ADR-001 — Stack Decision: Python + Anthropic SDK vs Alternatives
**Date:** 2026-04-18  
**Status:** Accepted  
**Decider:** Felix Andres Rios Blanco — OPERION

---

## Context

Agent 1 (TRIAGE) for Clever Fit Ingolstadt needs to:
1. Accept a text input (Instagram DM or WhatsApp message)
2. Detect language (DE/EN)
3. Classify intent
4. Generate an accurate, compliant response based on a verified knowledge base
5. Run locally on a Windows machine with a browser-based UI
6. Cost near-zero in Phase 0 (manual assist mode)

---

## Decision

**Use Python 3.12 + Anthropic SDK (Claude) + Flask for the Phase 0 mini web app.**

---

## Alternatives Considered

### Option A: Third-party chatbot builders (ManyChat, Tidio, Intercom)
- **Pro:** No-code, fast setup
- **Con:** Not GDPR-compliant by default for German data. Monthly cost €49–€299. No custom knowledge base control. Cannot customize escalation logic. Vendor lock-in. Cannot be white-labeled as OPERION IP.
- **Verdict:** Rejected. Violates GDPR requirements and OPERION's "we own the IP" principle.

### Option B: n8n + OpenAI
- **Pro:** Visual workflow builder, good for automation
- **Con:** OpenAI data may be used for training (GDPR risk). n8n adds complexity for Phase 0. Overkill for manual assist mode.
- **Verdict:** Rejected for Phase 0. Reconsidered for Phase 2 orchestration.

### Option C: LangChain + any LLM
- **Pro:** Flexible framework
- **Con:** Heavy dependency, fast-moving API, adds abstraction that obscures what the agent is doing. Harder to debug for a solo founder.
- **Verdict:** Rejected. Unnecessary complexity for this use case.

### Option D (Chosen): Python + Anthropic SDK + Flask
- **Pro:**
  - Full control over prompts, knowledge base, and escalation logic
  - Anthropic's data processing agreement is GDPR-compliant (EU data can stay in EU)
  - Claude excels at instruction-following and multilingual generation (DE/EN/ES)
  - Zero vendor lock-in — the logic is plain Python, portable to any infrastructure
  - Cost: ~$0.003 per response at current Claude pricing (negligible for <300 DMs/month)
  - Flask adds a simple browser UI with zero frontend framework overhead
  - The entire codebase becomes OPERION's reusable IP for future clients
- **Con:**
  - Requires Python environment setup (one-time, 15 minutes)
  - Claude API key needed (already have Anthropic subscription)
- **Verdict:** Accepted.

---

## Architecture (Phase 0)

```
[Felix opens browser: localhost:5000]
        ↓
[Pastes incoming DM text]
[Selects channel: Instagram / WhatsApp]
        ↓
[Flask app → agent.py]
        ↓
[Language detection: DE / EN]
[Intent classification]
        ↓
[Knowledge base lookup: knowledge_base.py]
        ↓
[Anthropic API: Claude generates response]
        ↓
[Response displayed with Copy button]
[Intent label shown: FAQ / Trial / Pricing / Escalate]
        ↓
[Felix reviews → copies → pastes in Instagram/WhatsApp]
[Interaction logged to SQLite]
```

---

## GDPR Compliance Notes

- No personal data (names, phone numbers) is stored. Only message text + intent classification + timestamp.
- Logs are anonymizable on request (per CLAUDE.md policy).
- All processing happens locally on Felix's machine in Phase 0 — data never leaves Germany.
- Anthropic API calls: text is sent to Anthropic's API. Anthropic's DPA covers GDPR compliance. No training on customer data under the API agreement.
- In Phase 1 (Meta API integration): Meta's GDPR compliance for German users requires using the official Meta Graph API, not third-party scraping tools. This ADR's stack supports that.

---

## Consequences

- Phase 0: Flask app runs locally. No server, no cloud cost.
- Phase 1: Same codebase deployed to a small VPS (€5/month Hetzner Germany) with webhook endpoints.
- Phase 2: Same codebase extended with scheduling, multi-client support, reporting.
- Every future OPERION client gets this same stack, customized with their knowledge base.

---

## Relaciones
- [[MASTER_BUSINESS_PLAN]] — Estrategia de negocio a la que sirve esta decisión de stack
- [[OPERATIONS_BLUEPRINT]] — Arquitectura de procesos que este stack implementa
- [[OPERION_PROCESS_MAP]] — Auditoría técnica que identificó gaps en este stack actual
- [[STRATEGY_V2/OPERION_Sovereign_Blueprint_v2]] — Blueprint técnico v2 construido sobre esta ADR
- [[docs/PRD_agent1_triage]] — Spec del primer agente construido sobre este stack
