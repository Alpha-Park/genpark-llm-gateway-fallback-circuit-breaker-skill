"""
LLM Gateway Fallback Router and Circuit Breaker.
Zero external dependencies, standard library only.
"""

import time
from typing import Dict, List, Any, Optional, Callable

class CircuitBreakerOpenException(Exception):
    pass

class LLMGatewayCircuitBreakerClient:
    """
    Implements 3-state Circuit Breaker (CLOSED, OPEN, HALF-OPEN)
    and automated waterfall model failover for LLM API calls.
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_sec
        # provider -> {state, failure_count, last_failure_time, success_count}
        self.breakers = {}

    def _get_breaker(self, provider: str) -> Dict[str, Any]:
        if provider not in self.breakers:
            self.breakers[provider] = {
                "state": "CLOSED",
                "failure_count": 0,
                "last_failure_time": 0.0,
                "consecutive_successes": 0
            }
        return self.breakers[provider]

    def check_state(self, provider: str) -> str:
        """Checks and potentially transitions circuit state."""
        b = self._get_breaker(provider)
        now = time.time()

        if b["state"] == "OPEN":
            if now - b["last_failure_time"] >= self.recovery_timeout:
                b["state"] = "HALF-OPEN"
                b["consecutive_successes"] = 0

        return b["state"]

    def record_success(self, provider: str):
        """Records successful response from provider."""
        b = self._get_breaker(provider)
        if b["state"] == "HALF-OPEN":
            b["consecutive_successes"] += 1
            if b["consecutive_successes"] >= 2:
                b["state"] = "CLOSED"
                b["failure_count"] = 0
        elif b["state"] == "CLOSED":
            b["failure_count"] = 0

    def record_failure(self, provider: str):
        """Records failure from provider and triggers trip if threshold reached."""
        b = self._get_breaker(provider)
        b["failure_count"] += 1
        b["last_failure_time"] = time.time()

        if b["state"] in ("CLOSED", "HALF-OPEN") and b["failure_count"] >= self.failure_threshold:
            b["state"] = "OPEN"

    def execute_with_failover(self, providers: List[str], call_func: Callable[[str], Any]) -> Dict[str, Any]:
        """
        Executes call_func across ordered provider list with circuit breaker awareness.
        Fails over instantly if circuit is OPEN or if execution raises an exception.
        """
        attempts = []
        for p in providers:
            state = self.check_state(p)
            if state == "OPEN":
                attempts.append({"provider": p, "status": "SKIPPED_CIRCUIT_OPEN"})
                continue

            try:
                result = call_func(p)
                self.record_success(p)
                attempts.append({"provider": p, "status": "SUCCESS"})
                return {
                    "status": "success",
                    "served_by": p,
                    "result": result,
                    "attempts": attempts
                }
            except Exception as e:
                self.record_failure(p)
                attempts.append({"provider": p, "status": f"FAILED: {str(e)}"})

        return {
            "status": "all_providers_failed",
            "served_by": None,
            "result": None,
            "attempts": attempts
        }
