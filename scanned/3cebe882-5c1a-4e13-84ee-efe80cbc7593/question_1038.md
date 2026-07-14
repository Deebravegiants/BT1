# Q1038: respond_signage_point reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach P2P message handler `respond_signage_point` and control one request's authorization context plus a second request that reuses cached state so that `FullNodeAPI.respond_signage_point` in `chia/full_node/full_node_api.py` executes a path where make `respond_signage_point` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_api.py:789 `FullNodeAPI.respond_signage_point`
- Entrypoint: P2P message handler `respond_signage_point`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `respond_signage_point` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/full_node/full_node_api.py:respond_signage_point` with different identities and assert auth state cannot bleed across them
