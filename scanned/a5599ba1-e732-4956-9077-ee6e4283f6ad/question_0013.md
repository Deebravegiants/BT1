# Q13: validate_block_merkle_roots mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `validate_block_merkle_roots` and control compact proofs, summarized state, and full-object substitution timing so that `validate_block_merkle_roots` in `chia/consensus/block_body_validation.py` executes a path where swap compact or summarized proof material into `validate_block_merkle_roots` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/block_body_validation.py:158 `validate_block_merkle_roots`
- Entrypoint: peer-supplied block, proof, or spend path reaching `validate_block_merkle_roots`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `validate_block_merkle_roots` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/consensus/block_body_validation.py:validate_block_merkle_roots` and assert summarized forms never bypass equivalent validation
