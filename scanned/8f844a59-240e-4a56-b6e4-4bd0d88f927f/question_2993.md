# Q2993: add_to_block_signatures_validated applies the wrong privilege boundary to a public route

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_block_signatures_validated` and control public RPC or WebSocket command arguments that select protected actions so that `PeerRequestCache.add_to_block_signatures_validated` in `chia/wallet/util/peer_request_cache.py` executes a path where reach a privileged path in `add_to_block_signatures_validated` from a nominally unprivileged public route or command shape, violating the invariant that unprivileged callers must not reach privileged daemon, keychain, or wallet actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:72 `PeerRequestCache.add_to_block_signatures_validated`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_block_signatures_validated`
- Attacker controls: public RPC or WebSocket command arguments that select protected actions
- Exploit idea: reach a privileged path in `add_to_block_signatures_validated` from a nominally unprivileged public route or command shape
- Invariant to test: unprivileged callers must not reach privileged daemon, keychain, or wallet actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: invoke `chia/wallet/util/peer_request_cache.py:add_to_block_signatures_validated` through its public command path with unprivileged inputs and assert privilege checks fail before state changes
