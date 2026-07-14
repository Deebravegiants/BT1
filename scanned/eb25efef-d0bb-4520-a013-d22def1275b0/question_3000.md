# Q3000: add_to_additions_in_block derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_additions_in_block` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `PeerRequestCache.add_to_additions_in_block` in `chia/wallet/util/peer_request_cache.py` executes a path where make `add_to_additions_in_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:88 `PeerRequestCache.add_to_additions_in_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_additions_in_block`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `add_to_additions_in_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/wallet/util/peer_request_cache.py:add_to_additions_in_block` and assert fork choice depends only on canonical validated state
