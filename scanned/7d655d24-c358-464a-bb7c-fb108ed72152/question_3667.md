# Q3667: add_key reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach RPC route `add_key` and control one request's authorization context plus a second request that reuses cached state so that `WalletRpcApi.add_key` in `chia/wallet/wallet_rpc_api.py` executes a path where make `add_key` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:829 `WalletRpcApi.add_key`
- Entrypoint: RPC route `add_key`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `add_key` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/wallet_rpc_api.py:add_key` with different identities and assert auth state cannot bleed across them
