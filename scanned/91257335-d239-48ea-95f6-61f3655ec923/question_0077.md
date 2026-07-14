# Q77: add_block_to_mmr reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `add_block_to_mmr` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `MMRManagerProtocol.add_block_to_mmr` in `chia/consensus/blockchain_interface.py` executes a path where reuse cache, dedup, or seen-set assumptions in `add_block_to_mmr` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/blockchain_interface.py:22 `MMRManagerProtocol.add_block_to_mmr`
- Entrypoint: peer-supplied block, proof, or spend path reaching `add_block_to_mmr`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `add_block_to_mmr` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/consensus/blockchain_interface.py:add_block_to_mmr` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
