# PRD — Agent 1: TRIAGE
**Client:** Clever Fit Ingolstadt  
**Version:** 1.0 | **Date:** 2026-04-18  
**Owner:** Felix Andres Rios Blanco — OPERION  
**Status:** Approved for development

---

## 1. Problem Statement

Clever Fit Ingolstadt receives inquiries via Instagram DMs and WhatsApp Business. Current response time: days, or never. The gym operates in a city with ~19,000 international students (THI) and thousands of Audi/MAN employees — a segment that writes in English and receives zero response in their language.

Every unanswered message is a lost member. At €29.90–49.90/month per membership, 20 unresponded inquiries/month = €600–€1,000 in lost MRR.

**Target:** Response time < 5 minutes. Language-matched. Accurate. No hallucinations.

---

## 2. Personas

| Persona | Language | Typical intent |
|---------|----------|---------------|
| Local German resident | DE | Pricing, hours, trial booking |
| THI international student | EN | Corporate rate? Trial? What to bring? |
| Audi / MAN employee | DE or EN | Corporate rate, FLEX plans |
| Short-term expat | EN | FLEX plan, no contract |

---

## 3. Phased Rollout

| Phase | Mode | Channel | When |
|-------|------|---------|------|
| 0 — Manual assist | Felix pastes DM → agent drafts → Felix copies & sends | Instagram DM + WhatsApp (manual) | Now |
| 1 — Semi-auto | Webhook receives DM → agent drafts → Felix approves in web app | Instagram Graph API + WhatsApp Business API | Post Meta access |
| 2 — Autonomous | Agent responds directly, logs everything, escalates edge cases | All channels | Month 3+ |

---

## 4. Functional Requirements

### 4.1 Language Detection
- Auto-detect DE or EN from input message
- If ambiguous or other language: respond in EN
- Never mix languages in a single response

### 4.2 Intent Classification
| Intent | Action |
|--------|--------|
| FAQ (hours, parking, address) | Respond directly from knowledge base |
| Pricing inquiry | Explain relevant plan(s), include hidden costs (Servicepauschale + Transponder) |
| Trial training request | Explain process, what to bring, recommend booking |
| Membership signup | Direct to online signup URL |
| Corporate rate (Audi/MAN/THI) | Explain Corporate Rate €29.90 + ALL-IN benefits, require valid ID |
| Cancellation request | Do NOT process. Escalate to gym (call reception) |
| Complaint | Acknowledge with empathy, escalate to Udo (call reception) |
| Unclear | Ask one clarifying question. After 2 unclear exchanges: escalate |

### 4.3 Knowledge Base (Verified — April 2026)

**Location & Access**
- Address: Neuburger Str. 65, 85057 Ingolstadt
- Parking: Free, exclusive spots on-site
- Hours: Mon–Fri 06:00–24:00 | Sat/Sun/Holidays 09:00–21:00

**Membership Plans**
| Plan | Price/month | Contract | Notes |
|------|------------|---------|-------|
| Student Basic / Early Bird | €19.50 | 12 months | Basic access, restricted hours |
| Oster-Special | €24.50 | 12 months | €0 signup fee (saves €40), welcome gift |
| BASIC | €29.90 | 12 months | Strength + cardio + drinks |
| ALL-IN | €39.90 | 12 months | Basic + solarium + massage beds + Clever Vibe + other clubs |
| BASIC FLEX | €39.90 | None | Month-to-month, cancel anytime |
| ALL-IN FLEX | €49.90 | None | All-In benefits, month-to-month |
| Corporate (Audi/MAN/THI) | €29.90 | 12 months | ALL-IN benefits at BASIC price. Valid ID required. |

**Hidden Costs (always disclose proactively)**
- Servicepauschale: €19.90 charged every 6 months (automatic)
- Transponder (access key): €19.90 one-time (unless waived by promo)
- Auto-renewal: 12-month contracts renew automatically. Must cancel in writing 1 month before end.

**All plans include:** Unlimited water + flavored concentrates

**Sign up online:** https://www.clever-fit.com/de/ → "Mitglied werden"

**Trial Training**
- Cost: Free, no commitment
- Booking: Recommended (online or phone)
- What to bring: Valid ID (mandatory) + large towel (mandatory) + clean indoor sports shoes + appropriate sportswear
- Note: No bags in gym area — use lockers. No training shirtless.

**Services**
- No traditional sauna
- Wellness: Solarium + hydraulic massage beds (20 min/day max) — ALL-IN & Corporate only
- No group classes (no Zumba/Yoga)
- Clever Vibe vibration platforms — ALL-IN & Corporate only
- Unlimited drinks — all plans

**Escalation**
- Cancellations, complaints, contract disputes: call gym reception (Udo)
- WhatsApp Business: +49 157 869 10903

### 4.4 Tone Rules
- German: formal Sie ("Guten Tag, vielen Dank für Ihre Nachricht...")
- English: formal but warm ("Thank you for reaching out...")
- Max 1 emoji per response, only if natural
- Zero corporate jargon ("synergy", "leverage", "journey")
- Always end with a clear next step for the customer

### 4.5 Hard Rules (never break)
- NEVER invent prices, hours, or policies not in the knowledge base
- NEVER process a cancellation request — always escalate
- NEVER summarize contract terms — direct to official documents or reception
- NEVER respond to legal questions — escalate immediately
- If unsure: "Ich erkundige mich kurz und melde mich gleich bei Ihnen." / "Let me check that and get back to you shortly."

---

## 5. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Response generation time | < 10 seconds |
| Language accuracy | > 95% correct detection |
| Intent accuracy | > 90% correct classification |
| GDPR compliance | No personal data stored beyond session. No third-party data sharing. |
| Escalation rate | < 20% of messages |

---

## 6. Success Metrics (Baseline vs Target)

| Metric | Baseline (today) | Target (Day 30) |
|--------|-----------------|----------------|
| Avg response time | Days / never | < 5 minutes |
| % messages responded | ~30% | 100% |
| Trial bookings/month | Unknown | Tracked from Day 1 |
| Escalation rate | — | < 20% |

---

## 7. Out of Scope (v1.0)
- Automated sending (Phase 0 is manual copy-paste)
- WhatsApp API integration (Phase 1)
- CRM integration
- Payment processing
- Multi-gym support

---

## Relaciones
- [[CORE_VISION]] — Doctrina de eficiencia que este agente implementa directamente
- [[OPERATIONS_BLUEPRINT]] — Procesos "Captación" y "Conversión" que este agente sirve
- [[OPERION_SERVICES_PROCESSES]] — Definición del servicio Agent 1 (TRIAGE) que este PRD especifica
- [[clients/clever-fit/CLAUDE]] — Primer despliegue en producción de este agente
- [[docs/ADR_001_stack]] — Decisión de stack que sigue la implementación de este PRD
- [[MASTER_BUSINESS_PLAN]] — Modelo de ingresos (tier €200/mes) que este agente soporta
