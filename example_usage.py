"""
Demonstration of genpark-llm-gateway-fallback-circuit-breaker-skill
"""

from client import LLMGatewayCircuitBreakerClient

def main():
    gateway = LLMGatewayCircuitBreakerClient(failure_threshold=2, recovery_timeout_sec=5.0)

    # Simulated provider pool
    provider_priority = ["primary_provider_a", "secondary_provider_b", "emergency_provider_c"]

    # Mock caller where primary fails
    def mock_llm_call(provider: str):
        if provider == "primary_provider_a":
            raise ConnectionError("Primary provider 503 Service Unavailable")
        return f"Response generated successfully by {provider}"

    print("=== FIRST EXECUTION (Primary will fail, fallback to secondary) ===")
    res1 = gateway.execute_with_failover(provider_priority, mock_llm_call)
    print(f"Served By: {res1['served_by']}")
    print(f"Attempts: {res1['attempts']}")

    print("\n=== SECOND EXECUTION (Primary fails second time, tripping circuit) ===")
    res2 = gateway.execute_with_failover(provider_priority, mock_llm_call)
    print(f"Served By: {res2['served_by']}")

    print("\n=== THIRD EXECUTION (Primary is now circuit OPEN, skipped instantly) ===")
    res3 = gateway.execute_with_failover(provider_priority, mock_llm_call)
    print(f"Served By: {res3['served_by']}")
    print(f"Attempts: {res3['attempts']}")

if __name__ == "__main__":
    main()
