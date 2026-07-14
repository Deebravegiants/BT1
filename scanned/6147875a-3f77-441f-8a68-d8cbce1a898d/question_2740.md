# Q2740: generate_m_of_n_proof mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_m_of_n_proof` and control compact proofs, summarized state, and full-object substitution timing so that `MofNMerkleTree.generate_m_of_n_proof` in `chia/wallet/puzzles/custody/custody_architecture.py` executes a path where swap compact or summarized proof material into `generate_m_of_n_proof` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/puzzles/custody/custody_architecture.py:143 `MofNMerkleTree.generate_m_of_n_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_m_of_n_proof`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `generate_m_of_n_proof` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/puzzles/custody/custody_architecture.py:generate_m_of_n_proof` and assert summarized forms never bypass equivalent validation
