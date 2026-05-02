# OPERION PROCESS MAP
**Auditoría técnica y operativa — Abril 2026**
**Metodología: Six Sigma / Lean — "Eficiencia a través de la sustracción"**

---

## SISTEMA ACTUAL: INVENTARIO COMPLETO

```
operion-web/          ← Next.js 16 (frontend público + dashboard)
OPERION_Agents/
  triage_app/       ← Python Flask + Groq API (agente activo)
  docs/             ← ADR y PRD
lib/schema.sql      ← PostgreSQL schema (diseñado, no desplegado)
```

---

## 1. FLUJO DE CAPTACIÓN (Lead Gen)

```
USUARIO
  └─► operion.xyz/[locale]
        └─► Hero: badge → h1 → sub → CTAs
              └─► [CTA "Deploy Your First Agent"]
                    └─► TallyButton.openPopup("KYBBAg")
                          └─► Tally.so popup (externo)
                                └─► Submission → Tally dashboard
                                      └─► ⚠ DEAD END: no webhook, no CRM, no email
```

**Gaps identificados:**
| Paso | Estado | Problema |
|------|--------|---------|
| Landing → Tally | ✅ Funciona | — |
| Tally → CRM | ❌ No existe | Lead capturado, nadie lo procesa |
| Tally → Email bienvenida | ❌ No existe | Zero nurturing post-signup |
| Analytics de conversión | ❌ No existe | No hay forma de medir CTR → submission |

**Verdict:** El embudo captura leads y los mata. El 100% del esfuerzo de conversión termina en un dashboard de Tally que se revisa manualmente.

---

## 2. PROCESO DE CIERRE Y ONBOARDING

```
ESTADO ACTUAL: MANUAL AL 100%

Lead en Tally → Felix lo lee → Felix responde por email → 
llamada de 60 min → Felix configura agente manualmente →
shadow mode 7 días → go-live → Felix monitorea
```

**Lo que existe en código:**
- `lib/schema.sql` — estructura multitenant diseñada, NO desplegada
- `lib/mock-data.ts` — datos ficticios de Clever Fit para el dashboard UI
- `lib/types.ts` — tipos TypeScript del modelo de datos

**Lo que NO existe:**
- Página de onboarding
- Formulario de discovery
- Flujo de pago (Stripe no implementado)
- Automatización post-signup

**Verdict:** Onboarding es papel. Ningún paso está automatizado. Escala 0.

---

## 3. CICLO DE VIDA DEL AGENTE

### 3a. TRIAGE Agent (Python — único agente activo)

```
INPUT: mensaje texto + canal
  └─► agent.py::detect_language(text)
        └─► regex keyword matching (23 palabras alemanas)
        └─► retorna "de" | "en"
  └─► agent.py::classify_intent(text)
        └─► keyword matching en cadena (cancellation → complaint → corporate → trial → signup → pricing → faq)
        └─► retorna uno de 7 intents
  └─► agent.py::generate_response(message, channel)
        └─► get_system_prompt(language) ← inyecta 800+ palabras de KB
        └─► groq.chat.completions.create(model="llama-3.1-8b-instant")
        └─► retorna dict {response, language, intent, intent_label, channel}
  └─► app.py::log_interaction()
        └─► sqlite3 INSERT (timestamp, channel, language, intent, message_length, escalated)
OUTPUT: JSON con respuesta + metadata
```

**Stack actual:**
| Componente | Herramienta | Latencia estimada |
|-----------|-------------|-------------------|
| Detección de idioma | Regex/keywords | ~1ms |
| Clasificación de intent | Keyword matching | ~1ms |
| Generación de respuesta | Groq llama-3.1-8b-instant | ~800–1200ms |
| Logging | SQLite3 | ~2ms |
| **Total end-to-end** | | **~800–1200ms** |

**Problemas técnicos:**
- `detect_language`: falla con mensajes mixtos o muy cortos (emoji, "Hallo!")
- `classify_intent`: keyword chain rota — si alguien escribe "kostet" no matchea "kosten" (regex incompleto)
- SQLite: conexiones abiertas/cerradas manualmente (no usa context manager)
- `get_system_prompt`: inyecta 800+ palabras en CADA llamada (consumo de tokens innecesario)
- No hay timeout en llamadas a Groq (request puede colgarse indefinidamente)

### 3b. Dashboard (Next.js — Command Center)

```
/dashboard → layout.tsx (dark theme, propio <html>)
           → page.tsx → mock-data.ts (datos hardcoded)
                      → lib/types.ts (TypeScript interfaces)
```

**Estado:** UI estática con datos ficticios. No hay conexión a base de datos real.

---

## 4. GESTIÓN MULTITENANT

```
ESTADO: DISEÑADA EN PAPEL

lib/schema.sql
  ├── tenants       (empresas cliente)
  ├── agents        (agentes por tenant)
  ├── channels      (IG/WA/email por agente)
  ├── knowledge_base(FAQs por tenant)
  ├── interactions  (log de mensajes)
  ├── escalations   (escalaciones)
  ├── weekly_reports(reportes semanales)
  └── content_drafts(cola de contenido)

tenant_metrics VIEW — KPIs agregados por tenant
set_updated_at() TRIGGER — automático
```

**Gap crítico:** El schema existe pero hay CERO código que lo use. El agente Python escribe en SQLite local (`logs.db`), no en PostgreSQL multitenant.

---

## DIAGNÓSTICO DE REDUNDANCIAS

### RUIDO TÉCNICO IDENTIFICADO

| Elemento | Archivo | Veredicto |
|---------|---------|-----------|
| `@mdx-js/loader` | package.json | ❌ MUERTO — no hay archivos .mdx en el repo |
| `@mdx-js/react` | package.json | ❌ MUERTO — nunca importado |
| `@next/mdx` | package.json | ❌ MUERTO — no está en next.config.ts |
| `noche`, `sol`, `papel`, `tierra` tokens | tailwind.config.ts | ❌ MUERTOS — todos los componentes usan hex directo |
| `fontFamily.mono` custom stack | tailwind.config.ts | ⚠️ SEMI-MUERTO — dashboard usa `font-mono` pero es el stack nativo de Tailwind |
| `proxy.ts` (naming) | root | ⚠️ CONVENCIÓN — debería llamarse `middleware.ts` |
| `operion_lockup_horizontal.svg` | public/ | ⚠️ OBSOLETO — reemplazado por OPERIONLogo inline |
| `README.md` | root | ⚠️ VACÍO — default de Next.js sin customizar |

### PROCESOS LÓGICOS REDUNDANTES

| Proceso | Costo | Veredicto |
|---------|-------|-----------|
| `detect_language` con 23 keywords | Frágil, ~0% costo | Reemplazar con Groq langdetect (1 token) |
| KB hardcoded en string de 800 palabras | ~600 tokens por request | Extraer a archivo externo, cachear |
| Conexiones SQLite manual open/close | Error-prone | Usar context manager `with sqlite3.connect()` |
| Blog posts hardcoded en TSX | Imposible escalar | Extraer a JSON/CMS |
| `lib/mock-data.ts` sin tipos en LogEntry.action | Inconsistente | Tipado estricto |

---

## REGLA 10/10: ANÁLISIS DE TIEMPO

| Proceso | % del tiempo de build/dev | Acción |
|---------|--------------------------|--------|
| MDX packages (instalación + análisis) | ~12% del tiempo de `npm install` | ❌ ELIMINAR |
| Legacy color tokens (CSS purge scan) | ~3% del build | ❌ ELIMINAR |
| 800+ palabras de KB en cada Groq call | ~15% de tokens innecesarios | ⚡ CACHEAR |

**Inversión del 10% ahorrado:** Reducir tokens del sistema prompt → latencia del agente de ~1100ms → ~750ms target.

---

## PLAN DE EJECUCIÓN

### Eliminar (sin debatir)
1. `@mdx-js/*` y `@next/mdx` del package.json
2. Tokens legacy de tailwind.config.ts
3. `fontFamily.mono` (usar stack nativo)

### Corregir (quirúrgico)
4. `proxy.ts` → `middleware.ts`
5. SQLite: usar context managers
6. `classify_intent`: completar keywords con regex `\b`
7. Groq timeout: añadir `timeout=10`

### Construir (post-limpieza)
8. KB → archivo separado con lazy load
9. Webhook Tally → endpoint Next.js → notificación a Felix
10. Dashboard → conectar a SQLite real del agente (puente temporal hasta PostgreSQL)

---

*Generado: Abril 2026 — OPERION*
*Próxima revisión: post-Sprint 1 (Mayo 2026)*

---

## Relaciones
- [[OPERATIONS_BLUEPRINT]] — Arquitectura de procesos objetivo contra la que se audita este mapa
- [[OPERION_SERVICES_PROCESSES]] — Definiciones de servicio de agentes referenciadas en esta auditoría
- [[docs/ADR_001_stack]] — Decisión de stack que gobierna la arquitectura Flask/SQLite actual
- [[docs/PRD_agent1_triage]] — Requisitos de producto que impulsan los fixes del Sprint 1
- [[clients/clever-fit/CLAUDE]] — Contexto de Clever Fit donde se identificaron los gaps
