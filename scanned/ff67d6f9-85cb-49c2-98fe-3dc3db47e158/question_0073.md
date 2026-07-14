# Q73: add_block_to_mmr mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `add_block_to_mmr` and control compact proofs, summarized state, and full-object substitution timing so that `Blockchain.add_block_to_mmr` in `chia/consensus/blockchain.py` executes a path where swap compact or summarized proof material into `add_block_to_mmr` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/blockchain.py:1117 `Blockchain.add_block_to_mmr`
- Entrypoint: peer-supplied block, proof, or spend path reaching `add_block_to_mmr`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `add_block_to_mmr` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/consensus/blockchain.py:add_block_to_mmr` and assert summarized forms never bypass equivalent validation
