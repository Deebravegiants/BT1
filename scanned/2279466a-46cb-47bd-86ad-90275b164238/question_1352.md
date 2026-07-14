# Q1352: new_signage_point reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_signage_point` and control one request's authorization context plus a second request that reuses cached state so that `FullNodeStore.new_signage_point` in `chia/full_node/full_node_store.py` executes a path where make `new_signage_point` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_store.py:709 `FullNodeStore.new_signage_point`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_signage_point`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `new_signage_point` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/full_node/full_node_store.py:new_signage_point` with different identities and assert auth state cannot bleed across them
