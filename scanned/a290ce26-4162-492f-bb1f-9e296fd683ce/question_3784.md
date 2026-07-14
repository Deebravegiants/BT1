# Q3784: verify_signature reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach RPC route `verify_signature` and control one request's authorization context plus a second request that reuses cached state so that `WalletRpcApi.verify_signature` in `chia/wallet/wallet_rpc_api.py` executes a path where make `verify_signature` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1889 `WalletRpcApi.verify_signature`
- Entrypoint: RPC route `verify_signature`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `verify_signature` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/wallet_rpc_api.py:verify_signature` with different identities and assert auth state cannot bleed across them
