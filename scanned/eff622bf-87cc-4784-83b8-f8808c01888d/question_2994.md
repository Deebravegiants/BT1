# Q2994: add_to_block_signatures_validated reuses authorization context across unrelated requests

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_block_signatures_validated` and control one request's authorization context plus a second request that reuses cached state so that `PeerRequestCache.add_to_block_signatures_validated` in `chia/wallet/util/peer_request_cache.py` executes a path where make `add_to_block_signatures_validated` carry one request's authorization context into another request that should be isolated, violating the invariant that authorization context from one request must not be reused for another requester or target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:72 `PeerRequestCache.add_to_block_signatures_validated`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_block_signatures_validated`
- Attacker controls: one request's authorization context plus a second request that reuses cached state
- Exploit idea: make `add_to_block_signatures_validated` carry one request's authorization context into another request that should be isolated
- Invariant to test: authorization context from one request must not be reused for another requester or target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: issue back-to-back public requests through `chia/wallet/util/peer_request_cache.py:add_to_block_signatures_validated` with different identities and assert auth state cannot bleed across them
