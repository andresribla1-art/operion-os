"""
OPERION_OS — Autonomous Decision Engine (ADE)
Phase 4 - Alpha
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
AUDIT_LOG = LOGS_DIR / "sovereignty_audit.log"
LOGS_DIR.mkdir(exist_ok=True)

# ── Loggers ──────────────────────────────────────────────────────────────────
_fmt = "%(asctime)s [%(levelname)s] %(message)s"
_datefmt = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(level=logging.INFO, format=_fmt, datefmt=_datefmt)
logger = logging.getLogger("OPERION_OS")

file_handler = logging.FileHandler(AUDIT_LOG, encoding="utf-8")
file_handler.setFormatter(logging.Formatter(_fmt, _datefmt))
logger.addHandler(file_handler)

# ── Constants ─────────────────────────────────────────────────────────────────
SUPERVISOR_HOUR_COST = 25.00  # USD — cost of one supervisor hour avoided


class AutonomousDecisionEngine:
    """ADE — core orchestrator for all OPERION agents."""

    def __init__(self):
        self.version = "0.1.0-alpha"
        self.phase = "Phase 4 - Alpha"
        self.active_agents: dict = {}
        self.total_savings: float = 0.0
        self._boot()

    # ── Boot ──────────────────────────────────────────────────────────────────

    def _boot(self):
        logger.info("[OPERION_OS] Motor de Autonomía Iniciado")
        logger.info(f"[OPERION_OS] Version: {self.version} | {self.phase}")
        logger.info(f"[OPERION_OS] Timestamp: {datetime.now(timezone.utc).isoformat()}")
        logger.info(f"[OPERION_OS] Audit log: {AUDIT_LOG}")

    # ── ROI tracking ──────────────────────────────────────────────────────────

    def _record_saving(self, action: str):
        self.total_savings += SUPERVISOR_HOUR_COST
        logger.info(
            f"[OPERION_OS] Ahorro generado: ${SUPERVISOR_HOUR_COST:.2f} | "
            f"Total acumulado: ${self.total_savings:.2f} | Accion: {action}"
        )

    # ── Core decision logic ───────────────────────────────────────────────────

    def process_event(self, event: dict) -> dict:
        """
        Evaluate an incoming event and act autonomously when criteria are met.

        Expected event schema:
            {
                "type": str,          # event type identifier
                "user_tier": str,     # optional — "premium" | "standard"
                "source": str,        # optional — originating channel / device
                "metadata": dict,     # optional — extra context
            }
        """
        event_type = event.get("type", "unknown")
        user_tier = event.get("user_tier", "standard")
        ts = datetime.now(timezone.utc).isoformat()

        logger.info(f"[OPERION_OS] Evento recibido: type={event_type} | user_tier={user_tier}")

        # ── Case 1: Unauthorized access — auto-authorize premium users ────────
        if event_type == "unauthorized_access":
            if user_tier == "premium":
                action = "AUTO_AUTHORIZED — usuario premium, acceso concedido sin intervencion humana"
                logger.info(f"[OPERION_OS] {action}")
                self._record_saving("unauthorized_access -> auto-authorize premium")
                return {
                    "status": "authorized",
                    "action": action,
                    "autonomous": True,
                    "timestamp": ts,
                }
            else:
                action = "ESCALATED — usuario no-premium, requiere revision humana"
                logger.warning(f"[OPERION_OS] {action}")
                return {
                    "status": "escalated",
                    "action": action,
                    "autonomous": False,
                    "timestamp": ts,
                }

        # ── Case 2: Equipment failure — open preventive maintenance ticket ────
        if event_type == "equipment_failure":
            equipment = event.get("metadata", {}).get("equipment", "unknown")
            ticket_id = f"MAINT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            action = (
                f"MAINTENANCE_TICKET_CREATED — equipo: {equipment} | "
                f"ticket: {ticket_id} | activado sin intervencion humana"
            )
            logger.info(f"[OPERION_OS] {action}")
            self._record_saving("equipment_failure -> preventive maintenance ticket")
            return {
                "status": "ticket_created",
                "ticket_id": ticket_id,
                "equipment": equipment,
                "action": action,
                "autonomous": True,
                "timestamp": ts,
            }

        # ── Default: unknown event type ───────────────────────────────────────
        action = f"UNHANDLED_EVENT — tipo '{event_type}' no reconocido, registrado para revision"
        logger.warning(f"[OPERION_OS] {action}")
        return {
            "status": "unhandled",
            "action": action,
            "autonomous": False,
            "timestamp": ts,
        }

    # ── Agent registry ────────────────────────────────────────────────────────

    def register_agent(self, agent_id: str, agent_instance) -> None:
        self.active_agents[agent_id] = agent_instance
        logger.info(f"[OPERION_OS] Agente registrado: {agent_id}")

    def dispatch(self, agent_id: str, payload: dict) -> dict:
        if agent_id not in self.active_agents:
            logger.warning(f"[OPERION_OS] Agente desconocido: {agent_id}")
            return {"status": "error", "message": f"Agent '{agent_id}' not registered"}
        logger.info(f"[OPERION_OS] Despachando tarea -> {agent_id}")
        return self.active_agents[agent_id].run(payload)

    def status(self) -> dict:
        return {
            "engine": "ADE",
            "version": self.version,
            "phase": self.phase,
            "active_agents": list(self.active_agents.keys()),
            "total_savings_usd": self.total_savings,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ── Simulation ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ade = AutonomousDecisionEngine()

    print("\n" + "=" * 60)
    print("  OPERION_OS -- Simulacion de 3 Eventos")
    print("=" * 60)

    events = [
        {
            "type": "unauthorized_access",
            "user_tier": "premium",
            "source": "clever_fit_app",
            "metadata": {"user_id": "CF-1042"},
        },
        {
            "type": "equipment_failure",
            "user_tier": "standard",
            "source": "sensor_grid",
            "metadata": {"equipment": "Treadmill #7 — Clever Fit Ingolstadt"},
        },
        {
            "type": "unauthorized_access",
            "user_tier": "standard",
            "source": "clever_fit_app",
            "metadata": {"user_id": "CF-2201"},
        },
    ]

    for i, event in enumerate(events, 1):
        print(f"\n[Evento {i}] type={event['type']} | user_tier={event['user_tier']}")
        result = ade.process_event(event)
        print(f"  > Resultado: {result['status'].upper()}")
        print(f"  > Autonomo:  {result['autonomous']}")

    print("\n" + "=" * 60)
    print(f"  AHORRO TOTAL GENERADO: ${ade.total_savings:.2f} USD")
    print(f"  Audit log guardado en: {AUDIT_LOG}")
    print("=" * 60 + "\n")
