# Q3679: delete_all_keys reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach RPC route `delete_all_keys` and control one request's authorization context plus a second request that reuses cached state so that `WalletRpcApi.delete_all_keys` in `chia/wallet/wallet_rpc_api.py` executes a path where make `delete_all_keys` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:947 `WalletRpcApi.delete_all_keys`
- Entrypoint: RPC route `delete_all_keys`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `delete_all_keys` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/wallet_rpc_api.py:delete_all_keys` with different identities and assert auth state cannot bleed across them
