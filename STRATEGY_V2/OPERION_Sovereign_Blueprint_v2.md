# OPERION — Sovereign Operations Blueprint v2.0
> **Classification:** Internal · Confidential  
> **Version:** 2.0 · **Date:** April 21, 2026  
> **Owner:** Felix Andres Rios Blanco — Founder & CEO  
> **Purpose:** Complete technical and operational architecture for OPERION's autonomous execution infrastructure

---

## I. SYSTEM PHILOSOPHY

### The Command Interface Principle

Every operational flow in OPERION terminates in a Command Interface — a discrete, auditable, executable action taken on a live system. Not a recommendation. Not a draft awaiting human review. An action: a message sent, an event created, a post published, a record updated.

The intelligence of the system is in the path from input to Command Interface. The output of that path is always a command.

**Decision topology rule:** If a decision node cannot resolve to a Command Interface within 2 exchanges, it escalates to the Human Review Queue — which is itself a Command Interface (specifically: `NOTIFY → PAUSE → AWAIT_APPROVAL`).

### Three Tiers of Execution Authority

| Tier | Authority level | Examples |
|---|---|---|
| **Tier 1 — Autonomous** | Executes immediately, no review | FAQ response, booking confirmation, report generation, content scheduling |
| **Tier 2 — Draft-and-Hold** | Creates action, holds for approval | Complaint responses containing empathy statements, content mentioning client by name, ad campaign creation |
| **Tier 3 — Escalate** | Notifies human, does not act | Refund requests, legal questions, press inquiries, agent errors |

Tier classification is set at deployment. The target state for a mature OPERION deployment is >90% Tier 1 volume.

---

## II. COMMAND INTERFACE ARCHITECTURE

### Defined Command Interfaces (CI Registry)

Each CI is a terminal action node in the decision graph. All agent logic paths must route to exactly one CI.

```
CI-001  SEND_MESSAGE        → Dispatch response via active channel (IG/WA/Email)
CI-002  CREATE_BOOKING      → Write calendar event + send confirmation to contact
CI-003  UPDATE_CRM          → Write interaction record to database
CI-004  PUBLISH_CONTENT     → Schedule or post to social platform via API
CI-005  GENERATE_REPORT     → Compile and deliver formatted analytics document
CI-006  DRAFT_OUTREACH      → Create outreach message draft in prospect pipeline
CI-007  NOTIFY_HUMAN        → Push alert to Felix with full context payload
CI-008  PAUSE_AND_HOLD      → Suspend action thread, log reason, await instruction
CI-009  CLOSE_THREAD        → Mark interaction resolved, archive with metadata
CI-010  FLAG_ANOMALY        → Log metric deviation, attach to weekly report queue
CI-011  UPDATE_KNOWLEDGE    → Write new entry to client knowledge base
CI-012  EXECUTE_WEBHOOK     → Fire external system trigger (future: physical hardware)
```

`CI-012` is the bridge to the robotic hardware layer. All physical world commands in Phase 3 will route through this interface.

---

## III. AGENT ARCHITECTURE v2.0

### Agent 1: TRIAGE

**Status:** Priority build — Clever Fit MVP  
**Execution authority:** Tier 1 (FAQ, booking) / Tier 2 (complaints) / Tier 3 (legal, billing)

**Decision topology:**

```
[INBOUND MESSAGE]
       ↓
  [LANGUAGE DETECT]
  DE | EN | ES | OTHER→EN
       ↓
  [INTENT CLASSIFY]  confidence threshold: 70%
       ↓
  ┌────────┬──────────┬────────────┬───────────┬──────────┐
  FAQ     BOOKING   COMPLAINT    CANCELLATION  SALES     UNCLEAR
  ↓        ↓          ↓            ↓            ↓         ↓
CI-001  CI-002      CI-002       CI-007        CI-003   [CLARIFY×2]
SEND    CREATE      SEND         NOTIFY        UPDATE    ↓
MSG     BOOKING     EMPATHY+     HUMAN         CRM      CI-007
        +CI-003     CI-003+                    +CI-007  NOTIFY
        UPDATE      CI-007                             HUMAN
        CRM         NOTIFY
```

**Knowledge base query:** Before generating any FAQ response, TRIAGE executes a semantic lookup against the client knowledge base. If confidence on retrieved answer < 80%, response template is: "I'll confirm that and get back to you within [X minutes]" → `CI-007 NOTIFY_HUMAN`.

**Memory:** Full conversation context retained for 24 hours. After 24h: summarize to single-paragraph record → `CI-003 UPDATE_CRM` → archive.

**GDPR rule:** No personal data (name, phone, email) stored in agent memory beyond 30 days. All retention controlled by the data layer, not the agent.

---

### Agent 2: CONTENT FACTORY

**Status:** Build Month 2  
**Execution authority:** Tier 1 (Pillar 2, 3 content after Day 90) / Tier 2 (Pillar 1 client data content)

**Decision topology:**

```
[CONTENT CALENDAR TRIGGER]
       ↓
  [READ CONTENT BRIEF]
  Pillar: Proof | Teach | Build
  Platform: TK | IG | LI | YT | X
       ↓
  [ANALYTICS FEEDBACK READ]
  → What format performed best last 7 days?
       ↓
  [GENERATE DRAFT]
  Hook → Body → CTA → Hashtags
  Bilingual if required
       ↓
  [PILLAR CHECK]
  ↓ Proof (client data)        ↓ Teach / Build
  CI-008 DRAFT+HOLD            CI-004 PUBLISH_CONTENT
  → CI-007 NOTIFY_HUMAN        (Tier 1 after Day 90)
```

**Quality gates (all must pass before CI-004):**
- Hook present in first line (text) or first 2 seconds (video)
- Exactly 1 CTA
- Character limits not exceeded
- OPERION sigil watermark included (video: bottom-right, 10% opacity)
- Bilingual grammar check passed on both language versions

---

### Agent 3: ANALYTICS SCOUT

**Status:** Build Month 3  
**Execution authority:** Tier 1 (all reporting functions)

**Decision topology:**

```
[SCHEDULED TRIGGER: Sun 20:00 / Mon 08:00 CET]
       ↓
  [DATA PULL]
  Meta Business Insights → 7d/30d metrics
  Instagram Insights API → followers, reach, engagement
  Google Analytics → website (when active)
  Internal DB → DM volume, response time, bookings
       ↓
  [ANOMALY DETECTION]
  Any metric delta > ±20% week-over-week?
  ↓ YES                     ↓ NO
  CI-010 FLAG_ANOMALY        Continue
  + CI-007 NOTIFY_HUMAN
       ↓
  [REPORT GENERATION]
  Client format: PDF, OPERION branded
  Internal format: Notion database entry
       ↓
  CI-005 GENERATE_REPORT
  → CI-001 SEND_MESSAGE (delivery)
```

---

### Agent 4: OUTREACH

**Status:** Build Month 4–5  
**Execution authority:** Tier 2 (all outreach drafts require Felix send)

**Prospect scoring model:**

| Dimension | Score 1–5 | Signal |
|---|---|---|
| Pain level | 1–5 | Unanswered DMs visible, low review response rate, no booking link |
| Payment capacity | 1–5 | Google Maps reviews count, Instagram follower count, website quality |
| Accessibility | 1–5 | Owner identifiable on LinkedIn, direct contact available |
| **Minimum threshold** | **≥12/15** | Below 12: add to cold pool, do not contact |

**3-touch sequence:**
1. Day 0: Personalized intro (reference specific business detail) → `CI-006 DRAFT_OUTREACH`
2. Day 3: Value follow-up (data point from their vertical) → `CI-006`
3. Day 7–14: Case study share (Clever Fit metrics) → `CI-006`
4. No response after touch 3: `CI-003 UPDATE_CRM` status="cold" → `CI-009 CLOSE_THREAD`

---

### Agent 5: OPERATIONS

**Status:** Build Month 6  
**Execution authority:** Tier 1 (internal tasks) / Tier 2 (documentation changes)

**Weekly execution loop:**

```
[SUNDAY 18:00 CET TRIGGER]
       ↓
  Pull all agent logs from past 7 days
  Calculate HDR per client
  Calculate OII score per client
  Flag any SLA breach (response >10min, report miss, autonomy <80%)
  Calculate API costs vs. budget
       ↓
  [BUDGET CHECK]
  Any agent >120% of monthly budget?
  ↓ YES              ↓ NO
  CI-007             Continue
  NOTIFY_HUMAN
       ↓
  [RETROSPECTIVE PREP]
  Generate Sunday ritual template for Felix
  → CI-001 SEND_MESSAGE (internal)
```

---

## IV. ROBOTIC MODULARITY FRAMEWORK

### The Hardware-Agnostic Principle

Every Command Interface OPERION defines today operates on software systems. The logic is identical regardless of the execution surface. `CI-001 SEND_MESSAGE` today fires a WhatsApp API call. In 2029, it fires a signal to a voice synthesis unit mounted on a reception kiosk.

The intelligence layer — intent classification, language detection, response generation, booking confirmation — is separated from the output hardware by a single abstraction layer: the Command Interface.

This is not a future plan. This is a present architecture decision. Every agent built in 2026 is built on the assumption that its CI outputs will be routed to different hardware in Phase 3.

### Phase 3 Hardware Target Stack (2028–2030)

| Hardware class | Use case | OPERION CI mapping |
|---|---|---|
| Humanoid reception units (gym/clinic front desk) | Greet clients, answer FAQ, log attendance | CI-001, CI-002, CI-003 |
| Voice kiosks (dental waiting rooms, gym lobbies) | Check-in, appointment confirmation, upsell | CI-001, CI-002 |
| IoT-triggered workflows (building entry sensors) | Member check-in, access log, alert generation | CI-003, CI-010, CI-012 |
| Digital signage command layer | Content display, real-time metrics | CI-004, CI-005 |

### The 2026 Advantage

Clients who deploy OPERION in 2026 will have, by 2029:
- 3+ years of domain-specific interaction data
- Tuned intent classification for their specific client base
- Proven escalation rules calibrated to their business edge cases
- Response patterns that reflect their brand voice

When the hardware cost curve drops to accessible SMB pricing (projected 2028–2030 based on Boston Dynamics, Figure AI, and Sanctuary AI cost trajectories), OPERION clients will not be starting from zero. They will be deploying proven behavioral architecture onto new execution hardware.

The software layer is the moat. The hardware is just the next interface.

### CI-012 EXECUTE_WEBHOOK — Physical Command Gateway

This interface, currently inactive, is the bridge to physical execution. Architecture:

```
[AGENT DECISION NODE]
       ↓
  CI-012 EXECUTE_WEBHOOK
       ↓
  [PAYLOAD CONSTRUCTION]
  {
    "command_type": "physical_action",
    "target_device": "[device_id]",
    "action": "[greet|direct|confirm|alert]",
    "context": {
      "language": "de|en|es",
      "customer_id": "[anonymized]",
      "intent": "[classified_intent]",
      "response_content": "[generated_response]"
    },
    "timestamp": "[ISO-8601]",
    "requires_confirmation": false
  }
       ↓
  [HARDWARE EXECUTION LAYER]
  → Voice synthesis
  → Display update
  → Access control trigger
  → Physical acknowledgment
```

The payload schema is finalized today. Hardware that speaks this interface in 2029 requires no agent re-architecture.

---

## V. OPERATIONAL IMMUNITY STANDARDS

### Definition

Operational Immunity is the state in which a client business's core operational functions continue executing at full capability without any human presence. No owner on-call. No staff on standby. No manual override required.

A fully immune deployment has zero operational single points of human failure.

### Immunity Test Protocol

Administered at Day 30 and quarterly thereafter. Five scenarios selected at random from the client's operational scope:

1. **Off-hours inbound message:** Send a test inquiry via Instagram DM at 23:00 on a Saturday. Measure response time and accuracy.
2. **Booking request:** Send a booking request via WhatsApp. Verify that a calendar event is created, a confirmation is sent, and no human was involved.
3. **Report delivery:** Disable all human access to reporting tools for 48 hours. Verify Monday report arrives correctly.
4. **Complaint scenario:** Submit a test complaint message. Verify the response acknowledgment goes out and the human escalation alert is triggered.
5. **Content publishing:** Verify the week's content was published on schedule without manual intervention.

**Pass/fail:** All 5 scenarios must execute correctly. Any failure is a deployment deficiency requiring root cause analysis and remediation within 48 hours.

### Immunity Grade Scale

| Grade | HDR | OII | Description |
|---|---|---|---|
| **Sovereign** | ≥90% | 100% | Full autonomous operation. Human role: exception review only. |
| **Operational** | 80–89% | 80% | Near-full autonomy. Minor human touchpoints remain. |
| **Transitional** | 70–79% | 60% | Automation running, shadow mode transitioning to autonomous. |
| **Deploying** | <70% | <60% | Active deployment phase. Target: exit within 14 days. |

All OPERION clients should reach **Operational** grade by Day 30 and **Sovereign** grade by Day 90.

---

## VI. DATA ARCHITECTURE

### Layer Stack

```
[INBOUND EVENTS]
WhatsApp · Instagram · Email · Webhook
       ↓
[TRIAGE AGENT]
Intent classification · Language detection
       ↓
[EVENT LOG] — SQLite (Phase 0–1) → PostgreSQL (Phase 2+)
{
  event_id, timestamp, channel, language,
  intent_classified, confidence_score,
  action_taken, ci_executed, resolution_status,
  response_time_ms, escalated_to_human,
  customer_id (anonymized hash)
}
       ↓
[ANALYTICS LAYER]
Weekly aggregation · Anomaly detection
       ↓
[REPORTING LAYER]
Client PDF · Internal Notion entry
```

### Retention Policy

| Data type | Retention | Basis |
|---|---|---|
| Full interaction records | 30 days | GDPR Art. 5(1)(e) storage limitation |
| Anonymized aggregates | Indefinite | No personal data; legitimate interest |
| Client knowledge base | Duration of contract + 90 days | Contractual |
| Performance reports | Indefinite | No personal data |

---

## VII. DEPLOYMENT RUNBOOK

### Day 1–2: Discovery

- 60-minute kickoff (Felix leads)
- Capture: business hours, services, pricing, target customer, languages, current pain points, existing tools
- Baseline metrics documented: response time, booking volume, follower count, engagement rate
- Access acquired: Instagram Business, WhatsApp Business, Google Calendar, Meta Business Suite

### Day 3–7: Configuration

- TRIAGE agent customized with client FAQ, booking flow, escalation contacts
- Knowledge base populated and verified
- MCP connections established and tested
- Agent deployed in shadow mode (agent executes, all CI-004+ actions require approval)

### Day 8–14: Shadow Mode Calibration

- All agent outputs reviewed for accuracy and tone
- Knowledge base gaps identified and filled
- Escalation rules stress-tested with edge case scenarios
- Client feedback session Day 10 (30 minutes)
- HDR measured in shadow mode — target >75% before go-live authorization

### Day 15: Sovereign Activation

- TRIAGE moves to Tier 1 autonomous execution
- Client notified: "Your execution system is active."
- Weekly reporting begins
- Human review queue active for Tier 2/3 scenarios

### Day 30: First Immunity Audit

- 5-scenario OII test administered
- HDR calculated from 30 days of production data
- Results presented to client (15-minute review)
- Upgrade conversation if appropriate (add CONTENT FACTORY or ANALYTICS SCOUT)

---

*OPERION_Sovereign_Blueprint_v2.md — v2.0 · April 21, 2026*  
*Owner: Felix Andres Rios Blanco*  
*Next review: July 2026*

---

## Relaciones
- [[OPERATIONS_BLUEPRINT]] — Blueprint v1 de procesos que este documento extiende técnicamente
- [[OPERION_SERVICES_PROCESSES]] — Definiciones de agentes que este blueprint formaliza como interfaces CI
- [[docs/ADR_001_stack]] — Decisión de stack sobre la que se construye la arquitectura Phase 0–2
- [[docs/PRD_agent1_triage]] — PRD del Agent 1 (TRIAGE) implementado bajo CI-001
- [[STRATEGY_V2/OPERION_Business_Plan_v2]] — Plan de negocio al que este blueprint sirve técnicamente
- [[archive/VISION_2031]] — Horizonte robótico 2029+ que el §9 de este blueprint referencia
