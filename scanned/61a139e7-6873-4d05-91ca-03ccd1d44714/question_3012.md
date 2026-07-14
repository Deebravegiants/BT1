# Q3012: sign_message reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sign_message` and control one request's authorization context plus a second request that reuses cached state so that `sign_message` in `chia/wallet/util/signing.py` executes a path where make `sign_message` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/util/signing.py:72 `sign_message`
- Entrypoint: wallet RPC or wallet sync flow reaching `sign_message`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `sign_message` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/util/signing.py:sign_message` with different identities and assert auth state cannot bleed across them
