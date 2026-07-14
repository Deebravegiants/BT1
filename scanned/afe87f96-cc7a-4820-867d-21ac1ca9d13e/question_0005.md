# Q5: add_block_record derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `add_block_record` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `AugmentedBlockchain.add_block_record` in `chia/consensus/augmented_chain.py` executes a path where make `add_block_record` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/augmented_chain.py:152 `AugmentedBlockchain.add_block_record`
- Entrypoint: peer-supplied block, proof, or spend path reaching `add_block_record`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `add_block_record` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/consensus/augmented_chain.py:add_block_record` and assert fork choice depends only on canonical validated state
