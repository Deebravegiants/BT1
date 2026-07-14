# Q575: new_proof_of_space mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach P2P message handler `new_proof_of_space` and control compact proofs, summarized state, and full-object substitution timing so that `FarmerAPI.new_proof_of_space` in `chia/farmer/farmer_api.py` executes a path where swap compact or summarized proof material into `new_proof_of_space` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/farmer/farmer_api.py:72 `FarmerAPI.new_proof_of_space`
- Entrypoint: P2P message handler `new_proof_of_space`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `new_proof_of_space` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/farmer/farmer_api.py:new_proof_of_space` and assert summarized forms never bypass equivalent validation
