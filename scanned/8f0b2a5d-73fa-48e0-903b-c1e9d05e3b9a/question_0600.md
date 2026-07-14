# Q600: respond_signatures reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach P2P message handler `respond_signatures` and control one request's authorization context plus a second request that reuses cached state so that `FarmerAPI.respond_signatures` in `chia/farmer/farmer_api.py` executes a path where make `respond_signatures` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/farmer/farmer_api.py:603 `FarmerAPI.respond_signatures`
- Entrypoint: P2P message handler `respond_signatures`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `respond_signatures` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/farmer/farmer_api.py:respond_signatures` with different identities and assert auth state cannot bleed across them
