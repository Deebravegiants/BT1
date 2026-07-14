# Q1071: signed_values reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach P2P message handler `signed_values` and control one request's authorization context plus a second request that reuses cached state so that `FullNodeAPI.signed_values` in `chia/full_node/full_node_api.py` executes a path where make `signed_values` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_api.py:1225 `FullNodeAPI.signed_values`
- Entrypoint: P2P message handler `signed_values`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `signed_values` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/full_node/full_node_api.py:signed_values` with different identities and assert auth state cannot bleed across them
