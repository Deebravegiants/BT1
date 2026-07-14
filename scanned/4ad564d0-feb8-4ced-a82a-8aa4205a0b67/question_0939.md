# Q939: request_proof_of_weight reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach P2P message handler `request_proof_of_weight` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `FullNodeAPI.request_proof_of_weight` in `chia/full_node/full_node_api.py` executes a path where reuse cache, dedup, or seen-set assumptions in `request_proof_of_weight` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:360 `FullNodeAPI.request_proof_of_weight`
- Entrypoint: P2P message handler `request_proof_of_weight`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `request_proof_of_weight` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/full_node/full_node_api.py:request_proof_of_weight` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
