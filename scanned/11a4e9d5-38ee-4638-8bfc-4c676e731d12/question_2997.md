# Q2997: add_to_additions_in_block mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_additions_in_block` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `PeerRequestCache.add_to_additions_in_block` in `chia/wallet/util/peer_request_cache.py` executes a path where interleave peak changes and rollback-sensitive inputs so `add_to_additions_in_block` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:88 `PeerRequestCache.add_to_additions_in_block`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_additions_in_block`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `add_to_additions_in_block` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/util/peer_request_cache.py:add_to_additions_in_block` with interleaved peaks and assert fork-local state never leaks across rollback
