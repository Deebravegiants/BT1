# Q1618: validate_weight_proof_inner mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_inner` and control compact proofs, summarized state, and full-object substitution timing so that `validate_weight_proof_inner` in `chia/full_node/weight_proof.py` executes a path where swap compact or summarized proof material into `validate_weight_proof_inner` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/weight_proof.py:1711 `validate_weight_proof_inner`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_inner`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `validate_weight_proof_inner` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/weight_proof.py:validate_weight_proof_inner` and assert summarized forms never bypass equivalent validation
