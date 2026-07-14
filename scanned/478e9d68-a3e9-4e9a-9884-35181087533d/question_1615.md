# Q1615: validate_weight_proof_inner reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_inner` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `validate_weight_proof_inner` in `chia/full_node/weight_proof.py` executes a path where reuse cache, dedup, or seen-set assumptions in `validate_weight_proof_inner` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/weight_proof.py:1711 `validate_weight_proof_inner`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_inner`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `validate_weight_proof_inner` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/full_node/weight_proof.py:validate_weight_proof_inner` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
