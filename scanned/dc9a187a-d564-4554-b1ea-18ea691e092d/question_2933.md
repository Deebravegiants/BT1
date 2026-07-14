# Q2933: generate_proof mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_proof` and control compact proofs, summarized state, and full-object substitution timing so that `MerkleTree.generate_proof` in `chia/wallet/util/merkle_tree.py` executes a path where swap compact or summarized proof material into `generate_proof` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/merkle_tree.py:97 `MerkleTree.generate_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_proof`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `generate_proof` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/wallet/util/merkle_tree.py:generate_proof` and assert summarized forms never bypass equivalent validation
