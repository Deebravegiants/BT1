# Q891: add_compact_vdf reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_compact_vdf` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `FullNode.add_compact_vdf` in `chia/full_node/full_node.py` executes a path where reuse cache, dedup, or seen-set assumptions in `add_compact_vdf` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:3331 `FullNode.add_compact_vdf`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_compact_vdf`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `add_compact_vdf` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/full_node/full_node.py:add_compact_vdf` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
