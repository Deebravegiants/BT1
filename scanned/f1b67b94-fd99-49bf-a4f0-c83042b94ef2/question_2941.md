# Q2941: check_merkle_proof reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `check_merkle_proof` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `check_merkle_proof` in `chia/wallet/util/merkle_utils.py` executes a path where reuse cache, dedup, or seen-set assumptions in `check_merkle_proof` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/merkle_utils.py:101 `check_merkle_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `check_merkle_proof`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `check_merkle_proof` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/wallet/util/merkle_utils.py:check_merkle_proof` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
