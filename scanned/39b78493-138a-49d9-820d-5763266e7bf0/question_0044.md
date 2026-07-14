# Q44: add_block derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `add_block` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `Blockchain.add_block` in `chia/consensus/blockchain.py` executes a path where make `add_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/blockchain.py:298 `Blockchain.add_block`
- Entrypoint: peer-supplied block, proof, or spend path reaching `add_block`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `add_block` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/consensus/blockchain.py:add_block` and assert fork choice depends only on canonical validated state
