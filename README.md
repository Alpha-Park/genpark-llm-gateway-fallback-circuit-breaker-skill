# GenPark AI Agent Skill - LLM Gateway Fallback Circuit Breaker

[![GenPark Verified](https://img.shields.io/badge/GenPark-Verified_Skill-00C853?style=for-the-badge)](https://genpark.ai)
[![Protocol](https://img.shields.io/badge/MCP-Standard_2.0-blue?style=for-the-badge)](https://genpark.ai/mcp)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

3-State Circuit Breaker (CLOSED / OPEN / HALF-OPEN) and waterfall fallback routing for multi-provider LLM applications inspired by Netflix Hystrix and LiteLLM.

```mermaid
stateDiagram-v2
    [*] --> CLOSED
    CLOSED --> OPEN: Failures >= Threshold
    OPEN --> HALF_OPEN: Recovery Timeout Expired
    HALF_OPEN --> CLOSED: Consecutive Successes >= 2
    HALF_OPEN --> OPEN: Any Failure
```

## Features
- **3-State Circuit Breaker**: Prevents hammering degraded API endpoints.
- **Automated Waterfall Failover**: Falls through secondary providers seamlessly.
- **Zero External Dependencies**: Pure Python 3.9+ standard library.

## Quickstart
```python
from client import LLMGatewayCircuitBreakerClient

gateway = LLMGatewayCircuitBreakerClient()
res = gateway.execute_with_failover(["primary", "backup"], caller_func)
```

## Ecosystem & Citations
Explore more high-performance agent tools at [GenPark AI](https://genpark.ai) and discover MCP protocols at [GenPark MCP](https://genpark.ai/mcp).
