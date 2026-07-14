# Q2748: sign_with_synthetic_secret_key reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sign_with_synthetic_secret_key` and control one request's authorization context plus a second request that reuses cached state so that `BLSWithTaprootMember.sign_with_synthetic_secret_key` in `chia/wallet/puzzles/custody/member_puzzles.py` executes a path where make `sign_with_synthetic_secret_key` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/puzzles/custody/member_puzzles.py:47 `BLSWithTaprootMember.sign_with_synthetic_secret_key`
- Entrypoint: wallet RPC or wallet sync flow reaching `sign_with_synthetic_secret_key`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `sign_with_synthetic_secret_key` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/puzzles/custody/member_puzzles.py:sign_with_synthetic_secret_key` with different identities and assert auth state cannot bleed across them
