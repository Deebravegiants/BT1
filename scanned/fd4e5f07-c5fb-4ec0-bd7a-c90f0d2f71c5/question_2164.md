# Q2164: add_lineage_proof reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_lineage_proof` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `CATLineageStore.add_lineage_proof` in `chia/wallet/cat_wallet/lineage_store.py` executes a path where reuse cache, dedup, or seen-set assumptions in `add_lineage_proof` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/cat_wallet/lineage_store.py:32 `CATLineageStore.add_lineage_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_lineage_proof`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `add_lineage_proof` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/wallet/cat_wallet/lineage_store.py:add_lineage_proof` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
