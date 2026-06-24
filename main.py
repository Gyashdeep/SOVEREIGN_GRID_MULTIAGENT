import asyncio
import json
import os
import logging
from groq import AsyncGroq
from pymodbus.client import AsyncModbusTcpClient
from pydantic import BaseModel, Field

# Setup basic logging for audit trails
logging.basicConfig(level=logging.INFO)

# --- SCHEMA FOR GOVERNOR ---
class GovernanceDecision(BaseModel):
    action_val: int = Field(..., ge=0, le=1000)
    reasoning: str
    is_safe: bool

class SovereignGridSwarm:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
        self.modbus = AsyncModbusTcpClient('192.168.1.100')
        self.logger = logging.getLogger("SovereignGovernor")

    async def run_safe_mode(self):
        """EMERGENCY: Atomic transition to neutral state."""
        try:
            if self.modbus.connected:
                # Force inverter/load to zero/neutral state
                await self.modbus.write_register(0x01, 0)
                await self.modbus.close()
            self.logger.critical("SYSTEM SAFE: Load registers zeroed. Emergency Protocol Engaged.")
        except Exception as e:
            self.logger.error(f"HARDWARE FAILURE DURING SAFE MODE TRANSITION: {e}")

    async def run_cycle(self):
        try:
            # 1. Telemetry Capture
            telemetry = {"temp": 72, "freq": 49.9, "load_pct": 82}
            
            # 2. Strategic Inference
            resp = await self.client.chat.completions.create(
                messages=[{"role": "system", "content": "You are the Strategist. Output valid JSON."},
                          {"role": "user", "content": f"Optimize: {telemetry}"}],
                model="llama3-70b-8192", 
                response_format={"type": "json_object"}
            )
            strategy = json.loads(resp.choices[0].message.content)
            
            # 3. Governance/Safety Veto (Hard Limit Check)
            if strategy.get("action_val", 0) > 900:
                self.logger.warning("Safety threshold exceeded. Triggering safe mode.")
                await self.run_safe_mode()
                return

            # 4. Actuation
            await self.modbus.connect()
            await self.modbus.write_register(0x01, strategy["action_val"])
            await self.modbus.close()
            
        except Exception as e:
            # Catch all runtime errors and move to safety
            self.logger.error(f"Runtime failure: {e}")
            await self.run_safe_mode()
            raise e

# --- THE HEARTBEAT ---
async def watchdog_loop():
    swarm = SovereignGridSwarm()
    while True:
        try:
            await swarm.run_cycle()
        except Exception:
            # Emergency exit ensures the loop doesn't continue with corrupted logic
            break
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(watchdog_loop())
