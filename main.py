import os
import uvicorn
import asyncio
from typing import Annotated, TypedDict, List
from operator import add
from fastapi import FastAPI
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage

# 1. State Definition
class GridState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    proposed_load: float
    is_safe: bool
    status: str

# 2. Physics Kernel
def physics_governor(proposed_load: float) -> bool:
    return 100.0 <= proposed_load <= 1000.0

# 3. Agent Nodes
def optimizer_agent(state: GridState):
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    # In production, pull real-time sensor data here
    return {"proposed_load": 450.0, "status": "optimized_request"}

def adversary_node(state: GridState):
    return {"proposed_load": 5000.0, "status": "adversarial_attack"}

def governor_node(state: GridState):
    is_safe = physics_governor(state["proposed_load"])
    return {"is_safe": is_safe, "status": "verified" if is_safe else "blocked"}

# 4. Graph Construction
DB_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/grid_db")
pool = ConnectionPool(conninfo=DB_URI)
checkpointer = PostgresSaver(pool)
checkpointer.setup()

workflow = StateGraph(GridState)
workflow.add_node("optimizer", optimizer_agent)
workflow.add_node("adversary", adversary_node)
workflow.add_node("governor", governor_node)
workflow.set_entry_point("optimizer")
workflow.add_edge("optimizer", "governor")
workflow.add_edge("adversary", "governor")
workflow.add_edge("governor", END)
app_graph = workflow.compile(checkpointer=checkpointer)

# 5. Background Control Loop (The "Heartbeat")
async def control_cycle():
    thread_id = "industrial_grid_001"
    while True:
        # This constant cycle ensures the system is always 'moving'
        app_graph.invoke({"messages": [HumanMessage(content="Orchestrate")]}, 
                         config={"configurable": {"thread_id": thread_id}})
        await asyncio.sleep(2) # Grid monitoring frequency (2 seconds)

# 6. Production API
api = FastAPI(title="AETHER-GOV Control Plane")

@api.on_event("startup")
async def startup_event():
    asyncio.create_task(control_cycle())

@api.get("/status/{thread_id}")
async def get_status(thread_id: str):
    state = checkpointer.get_tuple({"configurable": {"thread_id": thread_id}})
    return {"snapshot": state.snapshot if state else "No active session"}

if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=8000)
