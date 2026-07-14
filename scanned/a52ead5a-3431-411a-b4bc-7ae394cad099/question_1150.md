# Q1150: respond_compact_proof_of_time mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach P2P message handler `respond_compact_proof_of_time` and control compact proofs, summarized state, and full-object substitution timing so that `FullNodeAPI.respond_compact_proof_of_time` in `chia/full_node/full_node_api.py` executes a path where swap compact or summarized proof material into `respond_compact_proof_of_time` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:1729 `FullNodeAPI.respond_compact_proof_of_time`
- Entrypoint: P2P message handler `respond_compact_proof_of_time`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `respond_compact_proof_of_time` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/full_node_api.py:respond_compact_proof_of_time` and assert summarized forms never bypass equivalent validation
