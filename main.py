import asyncio
import os
import random
from typing import Annotated, TypedDict, List
from operator import add
from fastapi import FastAPI
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
def physics_governor(load: float) -> bool:
    return 100.0 <= load <= 1000.0

# 3. Nodes
def optimizer_node(state: GridState):
    # Simulate dynamic load requests
    load = random.randint(300, 1200) 
    return {"proposed_load": load, "status": "request_in_progress"}

def governor_node(state: GridState):
    is_safe = physics_governor(state["proposed_load"])
    return {"is_safe": is_safe, "status": "verified" if is_safe else "blocked"}

# 4. Graph Construction
DB_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/grid_db")
pool = ConnectionPool(conninfo=DB_URI)
checkpointer = PostgresSaver(pool)
checkpointer.setup()

workflow = StateGraph(GridState)
workflow.add_node("optimizer", optimizer_node)
workflow.add_node("governor", governor_node)
workflow.set_entry_point("optimizer")
workflow.add_edge("optimizer", "governor")
workflow.add_edge("governor", END)

app = workflow.compile(checkpointer=checkpointer)

# 5. Continuous Async Control Loop
async def run_continuous_grid():
    thread_id = "grid_stream_001"
    print("CORE-ISOLATE: Engine Started")
    while True:
        # Stream the execution to observe the 'movement'
        async for event in app.astream(
            {"messages": [HumanMessage(content="Next cycle")]},
            config={"configurable": {"thread_id": thread_id}}
        ):
            for node, values in event.items():
                print(f"Cycle Update | Node: {node} | Data: {values}")
        
        await asyncio.sleep(2) # Pulse rate: 2 seconds

api = FastAPI()

@api.on_event("startup")
async def startup():
    asyncio.create_task(run_continuous_grid())
