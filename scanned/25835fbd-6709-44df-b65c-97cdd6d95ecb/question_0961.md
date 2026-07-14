# Q961: request_block reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach P2P message handler `request_block` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `FullNodeAPI.request_block` in `chia/full_node/full_node_api.py` executes a path where reuse cache, dedup, or seen-set assumptions in `request_block` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:405 `FullNodeAPI.request_block`
- Entrypoint: P2P message handler `request_block`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `request_block` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/full_node/full_node_api.py:request_block` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
