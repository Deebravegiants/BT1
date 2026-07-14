# Q522: add_key_value reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `add_key_value` and control one request's authorization context plus a second request that reuses cached state so that `DataStore.add_key_value` in `chia/data_layer/data_store.py` executes a path where make `add_key_value` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/data_layer/data_store.py:710 `DataStore.add_key_value`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `add_key_value`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `add_key_value` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/data_layer/data_store.py:add_key_value` with different identities and assert auth state cannot bleed across them
