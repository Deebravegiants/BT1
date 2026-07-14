# Q72: add_block_to_mmr derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `add_block_to_mmr` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `Blockchain.add_block_to_mmr` in `chia/consensus/blockchain.py` executes a path where make `add_block_to_mmr` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/blockchain.py:1117 `Blockchain.add_block_to_mmr`
- Entrypoint: peer-supplied block, proof, or spend path reaching `add_block_to_mmr`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `add_block_to_mmr` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/consensus/blockchain.py:add_block_to_mmr` and assert fork choice depends only on canonical validated state
