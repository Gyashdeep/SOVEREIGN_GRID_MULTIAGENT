# Sovereign Grid-Agent
**Autonomous Multi-Agent Industrial Governor**

## Overview
The Sovereign Grid-Agent is a closed-loop, multi-agent swarm designed to govern critical industrial infrastructure. It optimizes energy arbitrage using Groq-powered reasoning while enforcing absolute physical safety via a hierarchical "Governor" architecture.

## Architecture


## Deployment
1. **Hardware:** Connect industrial PLC via Ethernet. Ensure a Hardware Watchdog Relay is wired to the server's pulse signal.
2. **Environment:** - Set `export GROQ_API_KEY='your_key_here'`
3. **Run Backend:** `python your_backend_file.py`
4. **Run Dashboard:** `streamlit run app.py`

## Safety Protocol
The system employs an immutable "Safety Veto" layer. Any action exceeding predefined temperature or frequency bounds is intercepted and vetoed by the Governor Agent. 
*Warning: This software controls physical hardware. Always test in Shadow Mode before activating write-access.*
