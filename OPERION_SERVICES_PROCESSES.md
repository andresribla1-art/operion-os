# OPERION — PROCESOS COMPLETOS DE SERVICIOS
**Versión:** 1.0 | **Fecha:** Abril 2026  
**Owner:** Felix Andres Rios Blanco — Founder & CEO  
**Clasificación:** Interno · Confidencial  

---

## ÍNDICE

1. [Agent 1 — TRIAGE (Recepcionista Digital)](#agent-1--triage)
2. [Agent 2 — CONTENT FACTORY (Máquina de Contenido)](#agent-2--content-factory)
3. [Agent 3 — ANALYTICS SCOUT (Inteligencia de Datos)](#agent-3--analytics-scout)
4. [Agent 4 — OUTREACH (Motor de Ventas)](#agent-4--outreach)
5. [Agent 5 — OPERATIONS (Sistema Nervioso Interno)](#agent-5--operations)
6. [Matriz de Escalaciones](#matriz-de-escalaciones)
7. [Ciclo de Onboarding de Cliente](#ciclo-de-onboarding-de-cliente)
8. [KPIs por Agente](#kpis-por-agente)

---

## AGENT 1 — TRIAGE
**"El que nunca duerme. El que nunca ignora."**  
**Estado:** ✅ Activo (Clever Fit Ingolstadt — Fase 0)  
**Stack:** Python 3.12 · Groq llama-3.1-8b-instant · Flask · SQLite  

---

### Propósito
Responder a cada mensaje entrante en menos de 5 minutos, en el idioma del cliente, con información 100% verificada. No reemplaza al humano — garantiza que ningún lead muera por silencio.

---

### Flujo de Proceso Completo

```
ENTRADA: Mensaje de texto (Instagram DM / WhatsApp / Email / Facebook)
│
├─► PASO 1: DETECCIÓN DE IDIOMA
│     Regex precompilado sobre 30+ marcadores léxicos alemanes
│     → "de" si ≥2 coincidencias con \b word boundaries
│     → "en" en todos los demás casos
│     Latencia: ~1ms
│
├─► PASO 2: CLASIFICACIÓN DE INTENCIÓN
│     Evaluación en cascada con regex \b (orden crítico):
│     1. cancellation  → palabras clave: kündigung, cancel, austritt...
│     2. complaint     → beschwerde, problem, unzufrieden...
│     3. corporate     → audi, man, thi, student, corporate...
│     4. trial         → probe, probetraining, kostenlos testen...
│     5. signup        → anmelden, sign up, mitglied werden...
│     6. pricing       → preis, kostet, how much, €, tarif...
│     7. faq           → (default — todo lo demás)
│     Latencia: ~1ms
│
├─► PASO 3: CONSTRUCCIÓN DEL SYSTEM PROMPT
│     get_system_prompt(language)
│     → Inyecta base de conocimiento verificada (~600 tokens)
│     → Añade channel_note según canal (Instagram: max 150 palabras)
│     → Reglas de tono: Sie formal (DE) / formal but warm (EN)
│
├─► PASO 4: GENERACIÓN DE RESPUESTA
│     groq.chat.completions.create(
│       model="llama-3.1-8b-instant",
│       max_tokens=512,
│       timeout=10
│     )
│     Latencia media: ~800–1200ms
│
├─► PASO 5: LOGGING
│     SQLite INSERT: timestamp · channel · language · intent
│                    message_length · escalated (0/1)
│     Latencia: ~2ms
│
└─► SALIDA: JSON {response, language, intent, intent_label, channel}
     Tiempo total end-to-end: ~800–1200ms
```

---

### Reglas de Negocio (Inviolables)

| Escenario | Acción del Agente |
|-----------|-------------------|
| FAQ (horarios, parking, dirección) | Responde directamente desde KB |
| Precios | Explica plan relevante + SIEMPRE menciona Servicepauschale (€19,90 c/6 meses) y Transponder (€19,90 único) |
| Probetraining | Explica proceso, qué traer, recomienda reservar |
| Signup | Dirige a clever-fit.com/de → "Mitglied werden" |
| Corporate (Audi/MAN/THI) | Explica tarifa €29,90 + beneficios ALL-IN, requiere ID válido |
| Cancelación | ❌ NUNCA procesar → escalar a recepción (Udo) |
| Queja | Reconocer con empatía → escalar a recepción |
| Incertidumbre | "Ich erkundige mich kurz..." / "Let me check that..." — solo si genuinamente inseguro |
| Pregunta legal | ❌ NUNCA responder → escalar inmediatamente |

---

### Fases de Despliegue

| Fase | Modo | Canal | Estado |
|------|------|-------|--------|
| 0 — Manual Assist | Felix pega DM → agente genera → Felix copia y envía | IG + WA (manual) | ✅ Activo |
| 1 — Semi-auto | Webhook recibe DM → agente genera → Felix aprueba en web app | IG Graph API + WA Business API | 🔄 Post-acceso Meta |
| 2 — Autónomo | Agente responde directamente, log completo, escala edge cases | Todos los canales | 📅 Mes 3+ |

---

### Base de Conocimiento Actual (Clever Fit Ingolstadt)

**Ubicación:** Neuburger Str. 65, 85057 Ingolstadt  
**Parking:** Gratuito, plazas exclusivas para miembros  
**Horarios:** Lun–Vie 06:00–24:00 | Sáb/Dom/Festivos 09:00–21:00  

**Planes:**
| Plan | Precio/mes | Contrato | Incluye |
|------|-----------|----------|---------|
| Student Basic / Early Bird | €19,50 | 12 meses | Acceso básico (horario restringido) |
| Oster-Special | €24,50 | 12 meses | €0 cuota de alta, regalo bienvenida |
| BASIC | €29,90 | 12 meses | Fuerza + cardio + bebidas |
| ALL-IN | €39,90 | 12 meses | BASIC + solarium + masajes + Clever Vibe + otros clubes |
| BASIC FLEX | €39,90 | Sin contrato | Como BASIC, cancelación mensual |
| ALL-IN FLEX | €49,90 | Sin contrato | Como ALL-IN, cancelación mensual |
| Corporate (Audi/MAN/THI) | €29,90 | 12 meses | Beneficios ALL-IN al precio BASIC |

**Costes ocultos (SIEMPRE revelar):**
- Servicepauschale: €19,90 automático cada 6 meses
- Transponder: €19,90 único (puede eliminarse por promoción)
- Renovación automática: contratos de 12 meses se renuevan solos, cancelar por escrito 1 mes antes

---

### Métricas Objetivo

| KPI | Baseline | Target Día 30 |
|-----|---------|--------------|
| Tiempo de respuesta promedio | Días / nunca | < 5 minutos |
| % mensajes respondidos | ~30% | 100% |
| Precisión de idioma | — | > 95% |
| Precisión de intención | — | > 90% |
| Tasa de escalación | — | < 20% |

---

## AGENT 2 — CONTENT FACTORY
**"Producción sin fricción. Una idea, diez formatos."**  
**Estado:** 📅 Build Mes 2  
**Stack:** Python · Anthropic API · Blotato MCP · Canva AI / DALL-E  

---

### Propósito
Transformar un brief de contenido único en 3+ piezas listas para publicar, adaptadas por plataforma, en DE/EN según mercado objetivo, con OPERION como marca paraguas.

---

### Flujo de Proceso Completo

```
ENTRADA: Content brief (tema + pilar + plataforma + locale)
│
├─► PASO 1: CONSULTA DE PIPELINE
│     Lee base de datos de contenido en Notion
│     → Obtiene próximo ítem programado
│     → Verifica pilar: Proof | Teach | Build
│     → Identifica plataformas: TikTok · IG · LinkedIn · YouTube · X
│
├─► PASO 2: LECTURA DE ANALYTICS
│     Consume reporte semanal de Agent 3 (Analytics Scout)
│     → Identifica formatos de mejor rendimiento (últimos 7 días)
│     → Ajusta longitud/formato basado en engagement reciente
│
├─► PASO 3: GENERACIÓN DE CONTENIDO
│     Para cada plataforma objetivo:
│     ├─ Texto: hook (≤2 segundos/primera línea) + cuerpo + CTA
│     ├─ Video: script con timestamps + visual cues + text overlays
│     └─ Carrusel: copy slide-by-slide + notas de diseño
│     Regla: 1 brief → mínimo 3 adaptaciones de plataforma
│
├─► PASO 4: ADAPTACIÓN DE TONO POR PLATAFORMA
│     TikTok    → Raw, personal, vulnerable. Felix en cámara.
│     Instagram → Pulido pero real. Datos + behind-the-scenes.
│     LinkedIn  → Thought leadership. Data-backed. Formato largo.
│     YouTube   → Deep-dive educativo. Screen recordings.
│     X/Twitter → Logs cortos de build-in-public. Métricas diarias.
│
├─► PASO 5: REVISIÓN HUMANA (Mes 1–3: obligatorio)
│     Presenta borrador a Felix → aprueba / solicita revisión
│     Criterios de calidad:
│     ✓ Hook en primeros 2 segundos (video) / primera línea (texto)
│     ✓ Exactamente 1 CTA
│     ✓ Dentro de límites de caracteres de la plataforma
│     ✓ Sin claims no verificados
│     ✓ Gramática correcta en AMBOS idiomas (si bilingüe)
│     ✓ Watermark OPERION sigil (bottom-right, 10% opacidad) en video
│
├─► PASO 6: PUBLICACIÓN VÍA BLOTATO MCP
│     POST /v2/posts con useNextFreeSlot:true o scheduledTime
│     → Sube media via presigned URLs
│     → Verifica estado: GET /v2/posts/{id}/status
│     → Registra URL y timestamp en Notion
│
└─► PASO 7: SEGUIMIENTO (Día 7 post-publicación)
     Agent 3 extrae: vistas · guardados · comentarios · shares
     → Actualiza base de datos de rendimiento
     → Retroalimenta al siguiente ciclo de generación
```

---

### Reglas de Contenido (Inviolables)

| Regla | Detalle |
|-------|---------|
| Modo Shadow (Mes 1–3) | Nunca publicar sin aprobación humana |
| Auto-publicación (Mes 4+) | Solo pilares Teach y Build. Pillar Proof SIEMPRE requiere aprobación |
| Watermark | Sigil OPERION, bottom-right, 10% opacidad, en todo video |
| Música | Solo Suno AI o librerías royalty-free. Nunca música con copyright |
| CTA obligatorio | Follow, save, comment, o link in bio — exactamente 1 por post |
| Datos de cliente | NUNCA en contenido público sin consentimiento escrito |
| Stock photos | PROHIBIDO — solo fotos reales, screenshots reales, datos reales |

---

### Pilares de Contenido (33% cada uno)

| Pilar | Tipo de Contenido | Plataformas Primarias |
|-------|------------------|-----------------------|
| **Proof** | Métricas Clever Fit, before/after, quotes de cliente | IG, LinkedIn, YouTube |
| **Teach** | How-to de agentes, frameworks, automatización local | TikTok, YouTube, LinkedIn |
| **Build** | Behind-the-scenes, código en pantalla, fracasos honestos | TikTok, X, IG Stories |

---

## AGENT 3 — ANALYTICS SCOUT
**"Los números no mienten. Los que no los miran, sí."**  
**Estado:** 📅 Build Mes 3  
**Stack:** Python · Meta Business Insights API · Adspirer MCP · Notion API  

---

### Propósito
Recolectar, procesar y entregar inteligencia de datos semanalmente a Felix y a cada cliente, con anomalías detectadas automáticamente y recomendaciones accionables.

---

### Flujo de Proceso Completo

```
TRIGGER: Domingo 20:00 CET (OPERION interno) / Lunes 08:00 CET (cliente)
│
├─► PASO 1: EXTRACCIÓN DE DATOS
│     Fuentes:
│     ├─ Meta Business Insights (via Adspirer MCP)
│     ├─ Instagram Insights API
│     ├─ Google Analytics (cuando aplique)
│     └─ SQLite local del agente (datos de TRIAGE)
│
├─► PASO 2: CÁLCULO DE MÉTRICAS
│     Para cada métrica, calcula:
│     ├─ Valor actual (semana)
│     ├─ Variación semana-a-semana (%)
│     └─ Variación mes-a-mes (%)
│
│     Métricas Clever Fit:
│     Seguidores · Alcance (7d) · Engagement rate · Volumen DMs
│     Tiempo respuesta promedio · Trial bookings · Autonomy rate
│     SLA breaches (respuestas >5 min)
│
│     Métricas OPERION:
│     Seguidores por plataforma · Vistas TikTok · Conexiones LinkedIn
│     Tamaño lista email · Signups waitlist · Contenido publicado
│     Pipeline de ventas (por etapa)
│
├─► PASO 3: DETECCIÓN DE ANOMALÍAS
│     Flag automático si métrica se mueve >20% en cualquier dirección
│     Alertas críticas:
│     ⚠ DM response time > 10 minutos
│     ⚠ Engagement rate < 1.5%
│     ⚠ Agent autonomy rate < 80%
│     ⚠ Presupuesto de API > 120% del target mensual
│
├─► PASO 4: GENERACIÓN DE REPORTE
│
│     REPORTE CLIENTE (Clever Fit):
│     Formato: PDF con branding OPERION
│     Contenido:
│     ├─ Executive summary (máximo 3 bullets)
│     ├─ Tabla de métricas clave
│     ├─ Top 3 posts por engagement
│     ├─ Anomalías detectadas
│     └─ Recomendaciones concretas (máximo 3)
│     Entrega: Email a gerente del gimnasio · Lunes 08:00 CET
│
│     REPORTE INTERNO (OPERION):
│     Formato: Entrada en base de datos Notion
│     Contenido: Números crudos · Sin diseño · Velocidad sobre pulido
│     Entrega: Notion update · Domingo 20:00 CET
│
└─► PASO 5: RETROALIMENTACIÓN A AGENT 2
     Escribe registro de rendimiento de contenido
     Agent 2 lo consume en su próximo ciclo de generación
```

---

### Retención de Datos

| Tipo de dato | Retención |
|-------------|-----------|
| Datos crudos de métricas | 90 días |
| Resúmenes agregados | Indefinido |
| Datos de interacciones (TRIAGE) | 30 días máximo (GDPR) |
| Reportes generados | Indefinido (archivados en Drive) |

---

## AGENT 4 — OUTREACH
**"10 mensajes perfectos valen más que 1.000 templates."**  
**Estado:** 📅 Build Mes 4–5  
**Stack:** Python · LinkedIn API · Anthropic API · Notion CRM  

---

### Propósito
Identificar prospects cualificados, investigar su negocio en profundidad, y generar mensajes de contacto hiperpersonalizados. Felix envía manualmente — el agente prepara todo.

---

### Flujo de Proceso Completo

```
TRIGGER: Nuevo prospect identificado por agente OR añadido manualmente por Felix
│
├─► PASO 1: INVESTIGACIÓN DEL PROSPECT
│     Fuentes de datos:
│     ├─ Instagram: seguidores, frecuencia de posts, tiempo de respuesta
│     │   (test enviando una pregunta como prospect anónimo)
│     ├─ Google Maps: cantidad de reseñas, rating promedio,
│     │   ¿responde a reseñas negativas?
│     ├─ Website: calidad visual, mobile-friendly, ¿tiene reservas online?
│     └─ LinkedIn: perfil del dueño/manager, posts recientes, company page
│
├─► PASO 2: SCORING
│     Puntuación 1–5 en tres dimensiones:
│     ├─ Nivel de dolor: ¿qué tan mal manejan su comunicación digital?
│     ├─ Capacidad de pago: indicadores de revenue (tamaño, ubicación, reseñas)
│     └─ Accesibilidad: ¿podemos contactar al decisor directamente?
│     Score total: suma de tres. Priorizar ≥ 12/15
│
├─► PASO 3: REDACCIÓN DE MENSAJE
│     Reglas absolutas:
│     ✓ SIEMPRE mencionar algo específico de su negocio
│     ✓ NUNCA usar templates genéricos
│     ✓ Mostrar el dolor, no el producto
│     ✓ Una sola CTA clara al final
│     Ejemplo de apertura correcta:
│     "Vi que tu estudio de yoga en Schwabing tardó 18 horas en responder
│      a una consulta de WhatsApp el martes pasado. Tenemos un agente
│      que lo hace en 4 minutos..."
│
├─► PASO 4: APROBACIÓN Y ENVÍO
│     Presenta borrador a Felix para revisión
│     Felix envía MANUALMENTE (LinkedIn — ToS enforcement)
│     O aprueba envío de email automatizado
│     Log en Notion: nombre · empresa · vertical · score · fecha · mensaje
│
└─► PASO 5: SECUENCIA DE SEGUIMIENTO
     Día 3:  Follow-up #1 — valor adicional (artículo, dato relevante)
     Día 7:  Follow-up #2 — caso de estudio Clever Fit (cuando esté publicado)
     Día 14: Follow-up #3 — cierre ("último contacto")
     Sin respuesta tras 3 toques → marcar "cold" → no reintentar
     Máximo 10 mensajes de outreach en frío por día
```

---

### Criterios de Cualificación de Prospect

| Vertical | Señales de Alta Prioridad |
|----------|--------------------------|
| Fitness Studio / Gym | >200 seguidores IG, <50% reseñas respondidas, no responde DMs |
| Salón / Barbería | Alto volumen de reseñas, sin booking online, WA sin respuesta rápida |
| Clínica Dental / Médica | Reseñas en español/inglés sin respuesta, website desactualizado |
| Restaurante / Café | Responde a reseñas negativas tarde o no responde, sin reservas online |
| Fisioterapia / Wellness | Agenda por teléfono solamente, no DMs activos |

---

## AGENT 5 — OPERATIONS
**"El sistema que mantiene al sistema."**  
**Estado:** 📅 Build Mes 6  
**Stack:** Python · Anthropic API · Notion API · Google Drive MCP  

---

### Propósito
Gestionar el tejido conectivo de OPERION: documentación, retrospectivas, costes de API, checklists de onboarding, y alertas de bloqueo para Felix.

---

### Flujo de Proceso Completo

```
PROCESOS CONTINUOS (background):
│
├─► MONITOREO DE COSTES API
│     Cada 24h: verifica consumo de Anthropic API, Blotato, Adspirer
│     Alerta si cualquier agente supera 120% del presupuesto mensual
│     Formato de alerta: "Agent 1 consumió €X.XX esta semana.
│                         Proyección mes: €XX. Budget: €XX."
│
├─► ACTUALIZACIÓN DE DOCUMENTACIÓN
│     Detecta cambios operativos → actualiza CLAUDE.md cuando corresponde
│     Mantiene OPERION_PROCESS_MAP.md actualizado con cambios reales
│     Versiona en GitHub (operion-core)
│
└─► TRACKING DE TAREAS
     Lee backlog en Notion · Detecta tareas vencidas >48h
     Notifica a Felix con contexto: qué está bloqueado y por qué

PROCESOS DISPARADOS POR EVENTOS:
│
├─► TRIGGER: Cliente firmó contrato
│     Genera checklist de onboarding personalizado:
│     Día 1–2:  Discovery (llamada 60 min · capturar horarios/precios/servicios)
│     Día 3–7:  Configuración TRIAGE para ese cliente
│     Día 8–14: Shadow mode + refinamiento
│     Día 15:   Go-live · Notificación al cliente
│     Día 30:   Primera revisión + oportunidad de upsell
│
├─► TRIGGER: Fin de semana (Domingo)
│     Genera plantilla de retrospectiva semanal:
│     ├─ ¿Qué funcionó? (con datos)
│     ├─ ¿Qué no funcionó? (con datos)
│     ├─ ¿Qué eliminamos la próxima semana?
│     └─ Nivel de energía del founder (1–10)
│     Si energía < 5 por 3 semanas consecutivas → alerta de burnout
│
└─► TRIGGER: Fin de mes
     Compila todas las métricas del mes (desde Agent 3)
     Compara actual vs target (KPIs del CLAUDE.md §6)
     Para cada KPI perdido >20%: inicia análisis "5 Whys"
     Para cada KPI superado >50%: documenta "qué funcionó"
```

---

## MATRIZ DE ESCALACIONES

| Escenario | Agente que detecta | Acción del Agente | Acción Humana requerida |
|-----------|-------------------|-------------------|------------------------|
| Queja de cliente | TRIAGE | Reconocer, empatía, escalar | Felix responde personalmente en <2h |
| Solicitud de reembolso o facturación | TRIAGE | Log, no procesar | Felix gestiona directamente |
| Consulta de prensa o media | TRIAGE | Log, no responder | Felix gestiona directamente |
| Pregunta legal (DSGVO, contrato) | TRIAGE | Log, no responder | Felix consulta asesor |
| Contenido que menciona cliente por nombre | CONTENT | Borrador, no publicar | Felix revisa y aprueba |
| Creación/cambio de campaña de ads | ANALYTICS | Borrador paused, no activar | Felix escribe "APPROVED" |
| Error o comportamiento inesperado de agente | Cualquiera | Log error, pausar tarea, notificar | Felix debuggea y reinicia |
| Cancelación de membresía | TRIAGE | Escalar a recepción (Udo) | Gym manager gestiona |
| Score prospect < 12/15 | OUTREACH | No contactar, archivar | — |
| Energía del founder < 5 (3 semanas) | OPERATIONS | Alerta de burnout | Felix toma semana de contenido off |

---

## CICLO DE ONBOARDING DE CLIENTE

```
FIRMA + PAGO SETUP FEE
│
├─► DÍA 1–2: DISCOVERY
│     Llamada 60 min (Felix lidera)
│     Capturar:
│     ├─ Horarios, servicios, precios, cliente objetivo
│     ├─ Idiomas, pain points actuales, herramientas existentes
│     └─ Accesos: IG Business · WA Business · Google Calendar · Meta Suite
│     Baseline de métricas capturado (Agent 3)
│
├─► DÍA 3–7: CONFIGURACIÓN
│     Agent 5 genera checklist personalizado
│     Configurar TRIAGE con:
│     ├─ Knowledge base específica del cliente
│     ├─ Flujo de booking adaptado a su calendario
│     └─ Reglas de escalación (¿quién es su "Udo"?)
│     Conectar MCP a sus plataformas
│     Deploy en shadow mode
│
├─► DÍA 8–14: SHADOW MODE
│     Cada respuesta del agente: Felix revisa antes de enviar
│     Sesión de feedback Día 10 (30 minutos)
│     Ajustar prompts, KB, y reglas según interacciones reales
│
├─► DÍA 15: GO-LIVE
│     Agent 1 pasa a modo autónomo
│     Cliente recibe: "Tu agente está activo" con resumen de capacidades
│     Weekly reports comienzan (Agent 3 · SOP-003)
│
└─► DÍA 30: PRIMERA REVISIÓN
     Llamada 30 min
     Presenta métricas mes 1 vs baseline
     Ajusta comportamiento del agente
     Evaluación de upsell: Agent 2 (Content) o Agent 3 (Analytics)
```

---

## KPIs POR AGENTE

| Agente | KPI | Target | Alerta |
|--------|-----|--------|--------|
| TRIAGE | Tiempo de respuesta | < 5 min | > 10 min |
| TRIAGE | Precisión de intención | > 90% | < 80% |
| TRIAGE | Tasa de escalación | < 20% | > 35% |
| TRIAGE | SLA breaches | 0 por semana | Cualquiera |
| CONTENT | Posts publicados/semana | ≥ 10 | < 5 |
| CONTENT | Engagement rate promedio | > 3% | < 1.5% |
| ANALYTICS | Entrega de reporte puntual | 100% | Cualquier fallo |
| OUTREACH | Prospects contactados/semana | 10 | < 5 |
| OUTREACH | Response rate | > 15% | < 8% |
| OPERATIONS | Tareas vencidas | 0 | Cualquiera >48h |
| OPERATIONS | Costes API vs budget | ≤ 100% | > 120% |

---

## STACK TECNOLÓGICO POR FASE

### Fase 0 — Foundation (€0/mes, Meses 1–3)
Python 3.12 · Groq API (llama-3.1-8b-instant) · Flask · SQLite · GitHub · Notion · Gmail · Canva · Tally

### Fase 1 — Growth (€50–150/mes, Meses 4–8)
+ Anthropic API (producción) · Blotato (scheduling) · Adspirer (ads analytics) · Twilio/Meta WA API · SumUp (facturación) · Hetzner VPS (€5/mes, Fráncfort)

### Fase 2 — Scale (€300–600/mes, Meses 9–18)
+ n8n Cloud (orquestación) · PostgreSQL/Supabase · Stripe · Wyoming LLC · Mercury Bank · Virtual Assistant (€400–600/mes)

---

*Documento generado: Abril 2026*  
*Próxima revisión operativa: Mayo 2026*  
*Cualquier cambio a este documento debe commitearse a operion-core con mensaje descriptivo.*

---

## Relaciones
- [[CLAUDE]] — Master OS que referencia este documento como spec de arquitectura de agentes
- [[CORE_VISION]] — Tesis de eficiencia que este sistema de cinco agentes ejecuta
- [[OPERATIONS_BLUEPRINT]] — Seis procesos de negocio que estos agentes sirven
- [[docs/PRD_agent1_triage]] — Spec funcional detallada para Agent 1 (TRIAGE)
- [[clients/clever-fit/CLAUDE]] — Despliegue en producción de TRIAGE + CONTENT FACTORY
- [[STRATEGY_V2/OPERION_Sovereign_Blueprint_v2]] — Interfaces de comando v2 y topologías de agentes
