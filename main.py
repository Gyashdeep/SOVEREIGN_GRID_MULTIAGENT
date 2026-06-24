import asyncio
import json
import random
import logging
import os
from groq import AsyncGroq
from pydantic import BaseModel, Field

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SovereignGovernor")

# --- MOCK HARDWARE LAYER ---
class MockModbus:
    async def write_register(self, addr, val):
        logger.info(f"[ACTUATOR] Register {addr} -> Value: {val}")

# --- GOVERNANCE SCHEMA ---
class GovernanceDecision(BaseModel):
    action_val: int = Field(..., ge=0, le=1000)
    reasoning: str

# --- CORE SIMULATION ENGINE ---
class SovereignGridSwarm:
    def __init__(self):
        # Ensure your API key is set in your terminal: export GROQ_API_KEY='your_key_here'
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.modbus = MockModbus()

    async def run_cycle(self):
        telemetry = {
            "temp": round(random.uniform(60, 90), 2),
            "load_pct": round(random.uniform(50, 95), 2)
        }
        
        # 1. Strategic Inference
        try:
            resp = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Return ONLY valid JSON with keys: action_val (int), reasoning (str)."},
                    {"role": "user", "content": f"Grid state: {telemetry}. Provide optimization."}
                ],
                model="llama3-70b-8192",
                response_format={"type": "json_object"}
            )
            strategy = json.loads(resp.choices[0].message.content)
            
            # 2. Safety Veto
            action_val = strategy.get("action_val", 0)
            if telemetry["temp"] > 85 or action_val > 900:
                logger.warning(f"VETO: Conditions unsafe (T={telemetry['temp']}). Forcing Zero.")
                await self.modbus.write_register(0x01, 0)
            else:
                await self.modbus.write_register(0x01, action_val)
                
        except Exception as e:
            logger.error(f"Inference Failure: {e}")

# --- WATCHDOG ---
async def watchdog_loop():
    swarm = SovereignGridSwarm()
    logger.info("SovereignGridSwarm: Initialization Complete.")
    while True:
        await swarm.run_cycle()
        await asyncio.sleep(2.0) # Increased sleep for API stability

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("CRITICAL: GROQ_API_KEY environment variable not found.")
    else:
        asyncio.run(watchdog_loop())
