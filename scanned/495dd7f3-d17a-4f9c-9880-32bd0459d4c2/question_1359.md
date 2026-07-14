# Q1359: new_peak reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_peak` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `FullNodeStore.new_peak` in `chia/full_node/full_node_store.py` executes a path where reuse cache, dedup, or seen-set assumptions in `new_peak` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_store.py:936 `FullNodeStore.new_peak`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_peak`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `new_peak` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/full_node/full_node_store.py:new_peak` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
