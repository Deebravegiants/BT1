# Q618: request_signed_values reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach P2P message handler `request_signed_values` and control one request's authorization context plus a second request that reuses cached state so that `FarmerAPI.request_signed_values` in `chia/farmer/farmer_api.py` executes a path where make `request_signed_values` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/farmer/farmer_api.py:723 `FarmerAPI.request_signed_values`
- Entrypoint: P2P message handler `request_signed_values`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `request_signed_values` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/farmer/farmer_api.py:request_signed_values` with different identities and assert auth state cannot bleed across them
