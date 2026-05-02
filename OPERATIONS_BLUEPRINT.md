# OPERION — OPERATIONS BLUEPRINT v2.0
**Sovereign Execution Operating System · Process Documentation**

> **Classification:** Internal · Confidential  
> **Version:** 2.0 — OPERION (post-rebrand)  
> **Date:** 21 April 2026  
> **Owner:** Felix Andres Rios Blanco  
> **Methodology:** Efficiency by Subtraction · Six Sigma / Lean  
> **Audit principle:** "Does removing this make the system stronger? If yes — it goes."

---

## ARCHITECTURE OVERVIEW: MULTITENANT SOVEREIGN STACK

### Philosophy

OPERION does not deploy tools. It deploys operational infrastructure. The distinction is architectural: a tool requires a human to operate it. Infrastructure operates autonomously and surfaces only results.

Every OPERION deployment follows the same principle: **total replacement of the operational human layer** for the processes within scope. Not augmentation. Replacement. The human shifts from operator to steward — reviewing results, setting direction, and handling the exceptions that require genuine judgment. Everything else is executed by the system.

### Multitenant database schema

Every client (tenant) operates in complete isolation. No data leaks. No cross-contamination.

```sql
-- CORE SCHEMA: operion_multitenant

CREATE TABLE tenants (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    slug        TEXT UNIQUE NOT NULL,
    vertical    TEXT CHECK (vertical IN ('gym','salon','clinic','restaurant','physio','other')),
    plan        TEXT CHECK (plan IN ('starter','growth','scale','founding')),
    status      TEXT CHECK (status IN ('onboarding','shadow','live','churned')),
    country     TEXT NOT NULL,  -- ISO 3166-1 alpha-2
    language    TEXT NOT NULL,  -- primary: 'de','en','es'
    fiscal_id   TEXT,           -- DE: Steuernummer | PE: RUC | CO: NIT
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    gdpr_consent_at TIMESTAMPTZ
);

CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenants(id) ON DELETE CASCADE,
    type            TEXT CHECK (type IN ('triage','content','analytics','outreach','operations')),
    status          TEXT CHECK (status IN ('shadow','autonomous','paused')),
    model           TEXT DEFAULT 'claude-sonnet-4-6',
    autonomy_rate   NUMERIC(5,2),   -- percentage of messages resolved without human
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE channels (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    UUID REFERENCES agents(id) ON DELETE CASCADE,
    type        TEXT CHECK (type IN ('instagram','whatsapp','email','facebook','tiktok')),
    handle      TEXT,
    credentials JSONB,  -- encrypted at rest via Supabase Vault
    active      BOOLEAN DEFAULT TRUE
);

CREATE TABLE knowledge_base (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   UUID REFERENCES tenants(id) ON DELETE CASCADE,
    category    TEXT,   -- 'pricing','hours','trial','parking','corporate','cancellation'
    question    TEXT,
    answer_de   TEXT,
    answer_en   TEXT,
    answer_es   TEXT,
    verified_at TIMESTAMPTZ,    -- only verified answers are injected into agent context
    verified_by TEXT
);

CREATE TABLE interactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenants(id),
    agent_id        UUID REFERENCES agents(id),
    channel         TEXT,
    language        TEXT,
    intent          TEXT,
    message_hash    TEXT,   -- SHA-256 of message for deduplication, NOT raw message
    response_time_ms INTEGER,
    escalated       BOOLEAN DEFAULT FALSE,
    autonomy_flag   BOOLEAN DEFAULT FALSE,   -- TRUE = resolved without human review
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    gdpr_purge_at   TIMESTAMPTZ GENERATED ALWAYS AS (created_at + INTERVAL '30 days') STORED
);

CREATE TABLE escalations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    interaction_id  UUID REFERENCES interactions(id),
    tenant_id       UUID REFERENCES tenants(id),
    reason          TEXT,   -- 'cancellation','complaint','low_confidence','unclear'
    notified_at     TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ,
    resolution      TEXT
);

CREATE TABLE content_drafts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenants(id),
    platform        TEXT,
    pillar          TEXT CHECK (pillar IN ('proof','teach','build')),
    caption_de      TEXT,
    caption_en      TEXT,
    caption_es      TEXT,
    status          TEXT CHECK (status IN ('draft','approved','scheduled','published','rejected')),
    scheduled_at    TIMESTAMPTZ,
    published_at    TIMESTAMPTZ
);

-- Aggregated KPI view per tenant (no raw personal data)
CREATE VIEW tenant_metrics AS
SELECT
    t.id,
    t.name,
    t.plan,
    COUNT(i.id)                                         AS total_interactions,
    AVG(i.response_time_ms)                             AS avg_response_ms,
    SUM(CASE WHEN i.escalated THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(i.id), 0) * 100                  AS escalation_rate_pct,
    SUM(CASE WHEN i.autonomy_flag THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(i.id), 0) * 100                  AS autonomy_rate_pct
FROM tenants t
LEFT JOIN interactions i ON i.tenant_id = t.id
    AND i.created_at > NOW() - INTERVAL '7 days'
GROUP BY t.id, t.name, t.plan;

-- Row-level security: tenants can only read their own data
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON interactions
    USING (tenant_id = current_setting('app.tenant_id')::UUID);
```

### Global fiscal consistency

Each tenant record stores `fiscal_id` (German Steuernummer, Peruvian RUC, Colombian NIT, Mexican RFC) and `country`. OPERION's reporting engine generates compliant invoices per jurisdiction:

- **Germany:** Kleinunternehmerregelung (§19 UStG) or standard VAT — configurable per tenant
- **Peru:** Factura electrónica (SUNAT SOAP) — Régimen MYPE or General
- **Colombia:** Factura electrónica DIAN
- **Mexico:** CFDI via PAC (Proveedor Autorizado de Certificación)

The same retainer amount flows through jurisdiction-specific tax logic automatically. No manual invoicing.

---

## PROCESS A — CAPTACIÓN & TRIAGE
**Lead Generation: From content touchpoint to agent-qualified lead**

### 🇪🇸 Flujo del proceso

| Paso | Acción | Agente / Humano | Tiempo |
|---|---|---|---|
| 1 | Prospecto encuentra OPERION vía TikTok, LinkedIn o Instagram | Contenido orgánico | — |
| 2 | Aterriza en operion.ai — Hero section activa el popup de Tally (Form ID: configurable) | Automático | <1s |
| 3 | Envío del formulario: nombre, vertical, ubicación, dolor principal | Automático (Tally) | — |
| **4** | **Webhook Tally → notificación push a Felix en <60 segundos** | **Automatizado** | **<60s** |
| 5 | Agent 4 ejecuta scoring automático: dolor (1–5) + capacidad de pago (1–5) + accesibilidad (1–5) | Agent 4: OUTREACH | <5 min |
| 6 | Si score ≥12/15: primer contacto personalizado (referenciando detalle específico del negocio) | Felix · manual | 1–4h |

### 🇬🇧 Human role replacement analysis

| Step | Previous human action | OPERION replacement | Time recovered |
|---|---|---|---|
| Manual Tally review | Felix checks dashboard every 2–4 hours | Webhook push notification in <60s | 1.5h/week |
| Manual prospect scoring | Felix researches each prospect manually | Agent 4 executes scoring from public data | 2h/week |
| Proposal construction | Felix builds ROI model manually (45 min/proposal) | Template with precalculated ROI calculator | 35 min/proposal |
| Discovery call (60 min) | Full 60 minutes unstructured | Pre-call form + 30-min structured call | 30 min/client |

**Human operations remaining:** Final first-contact message (personalized, not templated) and discovery call. Everything else is autonomous.

### Elimination Matrix — Process A

| Step | Verdict | Action | Sprint |
|---|---|---|---|
| Manual Tally lead review | **ELIMINATE** | Webhook Tally → push notification to Felix in <60s | Sprint 1 |
| Manual prospect scoring | **AUTOMATE** | Agent 4 executes automated scoring | Sprint 4 |
| Discovery call 60 min | **OPTIMIZE** | Pre-call form + 30-min structured call | Sprint 1 |
| Manual proposal build | **AUTOMATE** | Template + ROI calculator → 10 min total | Sprint 2 |

---

## PROCESS B — CONVERSIÓN & CIERRE
**Sales Conversion: From qualified prospect to signed agreement and setup fee payment**

### 🇩🇪 Prozessschritte

| Schritt | Aktion | Agent / Mensch | SLA |
|---|---|---|---|
| 1 | Prospektor antwortet auf Outreach → Discovery-Call-Buchung via Calendly | Manuell (Felix) | — |
| 2 | Pre-Call-Formular sendet Qualifizierungsdaten vor dem Anruf (Umsatz, DM-Volumen, Sprachen, Tools) | Automatisch | 24h vor Call |
| 3 | Discovery Call (30 min) — Felix leitet; erfasst Baseline-Metriken | Felix · manuell | 30 min |
| 4 | ROI-Kalkulation aus Template → Empfehlung Starter/Growth/Scale | 10 min | — |
| 5 | Angebot per E-Mail oder WhatsApp innerhalb von 24h | Felix | 24h |
| **6** | **IP-Bestätigung (schriftlich):** (a) Fallstudie erlaubt, (b) OPERION-Marke in Materialien, (c) Agent-Code ist OPERION IP | **Kritisch — nie überspringen** | 5 min |
| 7 | Zahlung des Setup-Betrags via Stripe (recurring ab Monat 1) | Automatisch | — |

### Total human role replacement target

After Phase 2: the only irreplaceable human steps in conversion are:
- The 30-minute discovery call (trust-building, not information-gathering)
- The IP agreement confirmation
- Final proposal approval before sending

Everything else — scoring, proposal generation, follow-up sequencing, invoice issuance, recurring billing — is autonomous.

### Elimination Matrix — Process B

| Step | Verdict | Action | Sprint |
|---|---|---|---|
| Discovery call 60 → 30 min | **OPTIMIZE** | Pre-qualifying form sent 24h before call | Sprint 1 |
| Manual proposal construction | **AUTOMATE** | Template with ROI calculator preconstruct | Sprint 2 |
| IP Agreement | **KEEP — NEVER REMOVE** | Legal protection for OPERION IP | — |
| Manual SumUp invoicing | **AUTOMATE** | Stripe recurring → eliminates 20 min/client/month forever | Sprint 3 |

---

## PROCESS C — ONBOARDING & IMPLEMENTACIÓN
**14-Day Deployment Cycle: From setup fee to agent go-live in autonomous mode**

### 🇬🇧 Phase 1 — Discovery (Day 1–2)

| Step | Action | Owner | Duration |
|---|---|---|---|
| 1 | Kickoff call (30 min — pre-form already completed) | Felix + client | 30 min |
| 2 | Access collection: IG Business · WA Business · Google Calendar · Meta Business Suite | Client sends credentials | SLA: 24h |
| 3 | Baseline metrics snapshot: current response time · DM volume · followers · trial bookings/month | Felix | 15 min |

### 🇬🇧 Phase 2 — Configuration (Day 3–7)

| Step | Action | Owner | Duration |
|---|---|---|---|
| 4 | Knowledge base build (verified hours, plans, hidden costs, trial process, escalation contacts) | Felix | 2h |
| 5 | TRIAGE agent configuration: intent rules, booking flow, escalation matrix | Felix | 1h |
| 6 | Shadow mode deploy: agent drafts every response, Felix approves before sending | Agent 1 + Felix | 0 autonomous messages |

### 🇬🇧 Phase 3 — Shadow Mode (Day 8–14)

| Step | Action | Owner | Duration |
|---|---|---|---|
| 7 | Real message processing: every DM processed, intent + response drafted | Agent 1 | Continuous |
| 8 | Day 10 feedback session (WhatsApp format, 10 min — not a call) | Felix + client | 10 min |
| 9 | Go-live decision criteria: >90% intent accuracy in last 48h · zero hallucinations · client confidence ≥7/10 | Felix | — |

### 🇬🇧 Phase 4 — Go-Live (Day 15)

| Step | Action | Owner |
|---|---|---|
| 10 | Autonomous mode activation: agent responds directly · escalation matrix active · full logging | Agent 1 |
| 11 | "Your agent is live" notification to client with capabilities summary and escalation contact | Felix |

### Human role post-go-live

After go-live, Felix's weekly time investment per client drops to approximately:
- **Shadow mode (Days 8–14):** 20 min/day review
- **Post go-live:** 30 min/week monitoring escalations + reviewing weekly report
- **Monthly:** 30-min review call + upsell evaluation

The agent handles 80%+ of all interactions autonomously. Felix handles exceptions.

### Elimination Matrix — Process C

| Step | Verdict | Action |
|---|---|---|
| Kickoff call 60 → 30 min | **OPTIMIZE** | Pre-form sent during signup → 30-min structured call | Sprint 1 |
| Access collection delays | **KEEP + SLA** | 24h SLA for client to send credentials — onboarding pauses until received | — |
| Shadow mode (7 days) | **KEEP — DO NOT SHORTEN** | Critical for trust and accuracy data. Minimum viable period. | — |
| Day 10 feedback call | **OPTIMIZE** | WhatsApp async format (10 min vs 30-min call) | Sprint 1 |

---

## PROCESS D — EJECUCIÓN SOBERANA (SOVEREIGN EXECUTION)
**24/7 Autonomous Agent Runtime: Technical orchestration and human role replacement**

### 🇪🇸 El objetivo central del Proceso D

**Reemplazar completamente el rol del recepcionista humano para todas las consultas de entrada.** No augmentar. No asistir. Reemplazar. El recepcionista humano gestiona: excepciones que requieren juicio real (quejas escaladas, solicitudes de cancelación, preguntas fuera del KB). Todo lo demás es el agente.

### Technical stack

| Component | Phase 0 | Phase 2 |
|---|---|---|
| **Runtime** | Python 3.12 + Flask · localhost:5000 | FastAPI · Hetzner VPS Frankfurt (€5–20/mo) |
| **LLM** | Groq llama-3.1-8b-instant · ~€0.003/response | Claude claude-sonnet-4-6 · structured output |
| **Storage** | SQLite (logs.db · local) | PostgreSQL/Supabase · multitenant schema · RLS |
| **Language detection** | Regex precompiled (30+ German markers) · ~1ms | Same + Spanish markers + confidence scoring |
| **Intent engine** | Cascade regex · 7 intents · <1ms | Cascade regex + LLM fallback for ambiguous messages |
| **Knowledge base** | Verified string (~600 tokens) injected per request | Per-tenant KB from PostgreSQL · Anthropic prompt caching |

### End-to-end message flow

```
POST /api/v1/tenant/{tenant_slug}/message
    ↓
1. Input validation (strip whitespace · reject empty · 400 on empty)
    ↓
2. Language detection
   GERMAN_MARKERS.findall(text) → ≥2 matches = "de"
   SPANISH_MARKERS.findall(text) → ≥2 matches = "es"
   else → "en"
   Time: ~1ms
    ↓
3. Intent classification (cascade regex — priority order)
   cancellation → complaint → corporate → trial → signup → pricing → faq
   Time: ~1ms
    ↓
4. Knowledge base retrieval (tenant-specific · language-matched)
   SELECT answer_{language} FROM knowledge_base
   WHERE tenant_id = $1 AND category = $2 AND verified_at IS NOT NULL
   Time: ~5ms
    ↓
5. System prompt construction
   get_system_prompt(language, tenant_slug) 
   + KB entries (~600 tokens)
   + channel_note (Instagram: max 150 words · WhatsApp: extended OK)
   = ~800-token system context
   Time: ~2ms
    ↓
6. LLM call (Claude API · structured output)
   max_tokens=512 · timeout=10s
   Hard rules enforced via prompt:
   - Never invent prices, hours, or policies
   - Always disclose hidden costs (Servicepauschale, etc.)
   - Never process cancellations — always escalate
   - If answer not in KB: "I'll check and get back to you" + escalate
   Time: ~800–1,200ms
    ↓
7. Escalation check
   IF intent IN (cancellation, complaint) OR confidence_flag:
     → INSERT escalations(interaction_id, reason, notified_at)
     → Push notification to Felix in <30s
   Time: ~2ms
    ↓
8. Logging (GDPR-compliant)
   INSERT interactions(tenant_id, agent_id, channel, language, intent,
                        message_hash, response_time_ms, escalated, autonomy_flag)
   Raw message text NEVER stored. Only SHA-256 hash.
   Time: ~2ms
    ↓
9. Response returned to caller
   {response, language, intent, intent_label, channel, response_time_ms}
Total: ~900–1,300ms end-to-end
```

### Human roles replaced by Process D

| Operational role | Previous state | OPERION replacement |
|---|---|---|
| **Front desk receptionist (FAQ)** | Human answering "what are the prices/hours/parking?" at €800–1,200/month | Agent responds in <5 min, 24/7, in customer's language |
| **Booking coordinator** | Human managing appointment requests via WhatsApp | Agent offers available slots from Google Calendar via MCP, confirms, logs |
| **Language interpreter** | No response to non-German/non-Spanish messages | Agent responds identically in DE, EN, and ES |
| **After-hours coverage** | Business inaccessible 8pm–8am | Agent fully operational 24/7 with zero overtime cost |
| **Response consistency** | Variable quality, human mood-dependent | Identical tone, accuracy, and compliance on every message |

### Elimination Matrix — Process D

| Component | Verdict | Action | Sprint |
|---|---|---|---|
| KB in system prompt (every request) | **OPTIMIZE** | Anthropic prompt caching → 90% token reduction for KB | Sprint 2 |
| Groq llama-3.1-8b | **KEEP Phase 0** | Switch to Claude API in Phase 1 for accuracy + GDPR compliance | Sprint 3 |
| SQLite logging | **MIGRATE** | PostgreSQL/Supabase in Phase 2. Schema designed. | Sprint 3 |
| Regex language detection edge cases | **OPTIMIZE** | Add Spanish markers + confidence threshold for <3-word messages | Sprint 2 |

---

## PROCESS E — GESTIÓN CENTRALIZADA (MULTITENANT COMMAND CENTER)
**Internal Command Center: Monitoring and managing thousands of clients from one interface**

### 🇩🇪 Architektur: Multimandanten-System

Das OPERION Command Center verwaltet alle Client-Instanzen über eine einzige Oberfläche. Kein manueller Datenbankzugriff. Kein Erinnerungsverlust zwischen Clients.

### Phase 0 → Phase 2 progression

**Phase 0 (Current — must be eliminated):**
- Dashboard at `/dashboard` shows Clever Fit client card with **hardcoded data from `lib/mock-data.ts`** — zero operational value
- Felix queries SQLite logs.db directly from terminal
- No push notification system for escalations
- Manual escalation handling with no SLA

**Phase 2 (Target — all manual processes replaced):**

| Component | Implementation | Replaces |
|---|---|---|
| **Live DB connection** | Dashboard reads from Supabase PostgreSQL multitenant schema in real time | Manual SQLite terminal queries |
| **Escalation push** | Complaint or cancellation intent → push to Felix's phone in <30s | Manual log scanning |
| **Agent cost monitor** | Daily API cost tracking per agent · alert if >120% monthly budget | No visibility |
| **Anomaly alerts** | Any KPI moving >20% triggers immediate notification | Weekly manual review |
| **Multi-tenant overview** | All clients on one screen: status, response time, autonomy rate, open escalations | Spreadsheet tracking |

### Multitenant isolation guarantees

Every tenant's data is isolated through three independent layers:

1. **Application layer:** `tenant_id` parameter required on every API call. Missing = 400 error.
2. **Database layer:** PostgreSQL Row-Level Security (RLS) policy enforces `tenant_id = current_setting('app.tenant_id')`. A bug in application code cannot cross tenant boundaries.
3. **Encryption layer:** Channel credentials (API keys, access tokens) stored in Supabase Vault (AES-256). Decrypted only at agent runtime, never logged.

### Dashboard components

```
OPERION COMMAND CENTER
├── 📊 Global Overview
│   ├── Total active clients: [n]
│   ├── Total interactions (7d): [n]
│   ├── Global avg response time: [n ms]
│   ├── Global escalation rate: [n%]
│   └── API cost (month-to-date): [€n]
│
├── 🔴 Open Escalations (live)
│   ├── [Tenant] [Channel] [Intent] [Received] [Status]
│   └── One-click to take over conversation
│
├── 📋 Client Cards (per tenant)
│   ├── Status: [shadow | autonomous | paused]
│   ├── Plan: [starter | growth | scale]
│   ├── Autonomy rate: [n%]
│   ├── Avg response time: [n ms]
│   ├── Interactions (7d): [n]
│   └── Last escalation: [timestamp]
│
└── 💰 Cost Monitor
    ├── API cost per agent (7d / 30d)
    ├── Cost per interaction (trend)
    └── Budget utilization (% of monthly cap)
```

### Elimination Matrix — Process E

| Component | Verdict | Action | Sprint |
|---|---|---|---|
| Dashboard mock data | **ELIMINATE** | Connect to real SQLite as bridge (Phase 0.5) → PostgreSQL Phase 2 | Sprint 2 |
| PostgreSQL schema | **DEPLOY NOW** | Schema designed; deploy to Supabase immediately | Sprint 2 |
| Manual escalation review | **AUTOMATE** | Push notification in <30s when intent = complaint/cancellation | Sprint 3 |

---

## PROCESS F — RETENCIÓN & ESCALADO (RETENTION & SCALE)
**Weekly reporting, client retention cadence, and upsell automation**

### 🇬🇧 Weekly report cycle (Agent 3 — Month 3+)

| Trigger | Time | Action | Recipient |
|---|---|---|---|
| **Sunday 20:00 CET** | Weekly | Agent 3 pulls all metrics · calculates WoW/MoM deltas · flags anomalies (>20% move) · writes to Notion | Felix (internal) |
| **Monday 08:00 CET** | Weekly | Branded PDF: 3-bullet exec summary + metrics table + top 3 posts + recommendations | Gym manager (client) |
| **Real-time** | On trigger | DM response >10 min · Engagement <1.5% · API cost >120% budget → push notification | Felix (immediate) |

### 🇪🇸 KPIs de retención monitoreados en vivo

| Métrica | Objetivo | Alerta |
|---|---|---|
| Tiempo promedio de respuesta | <5 min | >10 min |
| Precisión de clasificación de intención | >90% | <80% |
| Tasa de escalamiento | <20% | >35% |
| Tasa de autonomía | >80% | <65% |
| Brechas de SLA | 0/semana | Cualquiera |
| Costo API vs presupuesto | ≤100% | >120% |
| Entrega de informe | 100% puntual | Cualquier retraso |
| NPS del cliente | ≥8/10 | <6/10 |

### Monthly upsell evaluation

| Trigger | Condition | Action |
|---|---|---|
| Day 30 review call | Response time improved >80% vs baseline | Upsell window opens: Starter (€200) → Growth (€500) |
| Strong autonomy data | >80% autonomy rate in Month 1 | Present data: "80% of your messages are resolved without me. Adding Content (Agent 2) would do the same for your social media." |
| Low NPS (<6) | Any month | Felix calls personally within 24h. Do not send automated report. |

### Human roles replaced by Process F

| Task | Before OPERION | After OPERION |
|---|---|---|
| Weekly metrics collection | Felix queries Meta + IG API manually (2h/week) | Agent 3 pulls, calculates, and formats autonomously |
| Client report generation | Felix builds PDF manually (1.5h/week) | Agent 3 generates and sends branded PDF automatically |
| Anomaly detection | Felix notices something is wrong when client complains | Real-time alert system: Felix notified within minutes of any KPI deviation |
| Upsell identification | Felix manually evaluates each client monthly | System flags upsell window when metrics thresholds are crossed |

### Elimination Matrix — Process F

| Step | Verdict | Action | Sprint |
|---|---|---|---|
| Manual weekly report (2h/week) | **AUTOMATE** | Agent 3 generates and sends automatically · Sunday 20:00 | Sprint 4 |
| Day 30 review call (30 min) | **KEEP** | Upsell window + relationship maintenance. Minimum viable. | — |
| IP Agreement | **KEEP — CRITICAL** | Legal protection for OPERION IP. Never remove. | — |
| Manual upsell pitch | **TEMPLATIZE** | ROI template with Month 1 data auto-inserted | Sprint 3 |

---

## APPENDIX — MASTER ELIMINATION MATRIX

All processes evaluated against the Subtraction Principle.

| Process | Step | Verdict | Action | Time Recovered | Sprint |
|---|---|---|---|---|---|
| **A** | Manual Tally lead review | ❌ ELIMINATE | Webhook Tally → push notification <60s | 1.5h/week | Sprint 1 |
| **A** | Manual prospect scoring | 🤖 AUTOMATE | Agent 4 executes scoring automatically | 2h/week | Sprint 4 |
| **B** | Discovery call 60 min | ⚡ OPTIMIZE | Pre-call form → 30 min | 30 min/client | Sprint 1 |
| **B** | Manual proposal build | 🤖 AUTOMATE | Template + ROI calculator preconstruct | 45 min/proposal | Sprint 2 |
| **B** | Manual SumUp invoicing | 🤖 AUTOMATE | Stripe recurring → automated forever | 20 min/client/mo | Sprint 3 |
| **C** | Kickoff call 60 min | ⚡ OPTIMIZE | Pre-form + 30 min call | 30 min/client | Sprint 1 |
| **C** | Shadow mode 7 days | ✅ KEEP | Critical for trust and accuracy. Minimum viable. | — | — |
| **D** | KB tokens in every request | ⚡ OPTIMIZE | Anthropic prompt caching → 90% reduction | ~15% token cost | Sprint 2 |
| **D** | SQLite logs | 🤖 MIGRATE | PostgreSQL/Supabase in Phase 2 | Tech debt | Sprint 3 |
| **E** | Dashboard mock data | ❌ ELIMINATE | Connect to real DB immediately | 0 real value → eliminated | Sprint 2 |
| **E** | Manual escalation review | 🤖 AUTOMATE | Push notification in <30s | Variable/urgent | Sprint 3 |
| **F** | Manual weekly report | 🤖 AUTOMATE | Agent 3 generates and sends automatically | 2h/week | Sprint 4 |
| **F** | IP Agreement | ✅ KEEP — CRITICAL | Legal protection. Never remove. | — | — |

### Time recovery summary

| Category | Current (manual) | Post-audit (automated) | Reduction |
|---|---|---|---|
| Lead management | 3.5h/week | 0.5h/week | −86% |
| Sales process | 2.5h/week | 1h/week | −60% |
| Reporting | 2h/week | 0h/week | −100% |
| **Total recovered** | **8h/week** | **1.5h/week** | **−81%** |

### Sprint roadmap

| Sprint | Month | Primary goal | Human hours saved |
|---|---|---|---|
| **Sprint 1** | May 2026 | Webhook Tally + pre-call forms | 3h/week immediately |
| **Sprint 2** | Jun 2026 | Dashboard live data + proposal template + KB caching | +2h/week |
| **Sprint 3** | Jul 2026 | PostgreSQL migration + Stripe + push escalation alerts | +1.5h/week |
| **Sprint 4** | Aug 2026 | Agent 3 (Analytics) + Agent 4 (Outreach) fully autonomous | +2h/week |

---

## HUMAN-IN-THE-LOOP ESCALATION MATRIX

The only interactions that require human judgment — everything else is autonomous.

| Scenario | Agent action | Human SLA |
|---|---|---|
| Customer complaint | Acknowledge empathy · log · escalate | Felix reviews within 2h and responds personally |
| Cancellation request | Log · do NOT process | Felix handles directly with client |
| Refund or billing request | Log · do not process | Felix handles directly |
| Press or media inquiry | Log · do not respond | Felix handles directly |
| Legal question (DSGVO/contract) | Log · do not respond | Felix consults legal |
| Content mentioning client by name | Draft · do not publish | Felix reviews and approves |
| Ad campaign or budget change | Draft campaign paused · do not activate | Felix reviews and activates |
| Agent error or unexpected behavior | Log error · pause task · push notify | Felix debugs in <1h |
| Confidence <70% on intent | Respond with clarifying question | If still unclear after 2 exchanges → escalate |

---

## SOVEREIGNTY CLAUSE

Every process that remains in this system after this audit must earn its place.

The question is not "is this useful?" — the question is "does removing this make OPERION stronger, faster, or more profitable?" If the answer is yes: it goes. No exceptions.

> OPERION means *to operate*. Not to plan operating. Not to optimize the planning of operating. To operate.

---

*Document version: 2.0 — OPERION (post-rebrand)*  
*Date: 21 April 2026 · Next audit: 21 July 2026*  
*Methodology: Efficiency by Subtraction · Six Sigma / Lean*

---

## Relaciones
- [[CLAUDE]] — Master OS que gobierna todas las decisiones de proceso aquí
- [[CORE_VISION]] — Doctrina de eficiencia subyacente a estos seis procesos
- [[MASTER_BUSINESS_PLAN]] — Estrategia que este blueprint operacionaliza
- [[OPERION_SERVICES_PROCESSES]] — KPIs por agente y matriz de escalación
- [[OPERION_PROCESS_MAP]] — Auditoría técnica y análisis de gaps del estado actual
- [[docs/PRD_agent1_triage]] — Spec funcional para el proceso del agente TRIAGE
- [[clients/clever-fit/CLAUDE]] — Primera instanciación en producción de estos procesos
- [[STRATEGY_V2/OPERION_Sovereign_Blueprint_v2]] — Arquitectura técnica v2 que extiende este blueprint
