# Q2517: generate_unsigned_spendbundle reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_unsigned_spendbundle` and control one request's authorization context plus a second request that reuses cached state so that `NFTWallet.generate_unsigned_spendbundle` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `generate_unsigned_spendbundle` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:623 `NFTWallet.generate_unsigned_spendbundle`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_unsigned_spendbundle`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `generate_unsigned_spendbundle` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/nft_wallet/nft_wallet.py:generate_unsigned_spendbundle` with different identities and assert auth state cannot bleed across them
