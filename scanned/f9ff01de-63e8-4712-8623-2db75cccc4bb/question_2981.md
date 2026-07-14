# Q2981: add_to_block_requests reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_to_block_requests` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `PeerRequestCache.add_to_block_requests` in `chia/wallet/util/peer_request_cache.py` executes a path where reuse cache, dedup, or seen-set assumptions in `add_to_block_requests` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/peer_request_cache.py:49 `PeerRequestCache.add_to_block_requests`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_to_block_requests`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `add_to_block_requests` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/wallet/util/peer_request_cache.py:add_to_block_requests` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
