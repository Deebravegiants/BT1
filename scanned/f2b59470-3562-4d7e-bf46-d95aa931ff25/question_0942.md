# Q942: request_proof_of_weight mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach P2P message handler `request_proof_of_weight` and control compact proofs, summarized state, and full-object substitution timing so that `FullNodeAPI.request_proof_of_weight` in `chia/full_node/full_node_api.py` executes a path where swap compact or summarized proof material into `request_proof_of_weight` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:360 `FullNodeAPI.request_proof_of_weight`
- Entrypoint: P2P message handler `request_proof_of_weight`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `request_proof_of_weight` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/full_node_api.py:request_proof_of_weight` and assert summarized forms never bypass equivalent validation
