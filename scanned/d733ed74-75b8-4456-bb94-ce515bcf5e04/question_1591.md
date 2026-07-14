# Q1591: validate_weight_proof_single_proc trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc` and control block, header, proof, or weight fields supplied over the peer protocol so that `WeightProofHandler.validate_weight_proof_single_proc` in `chia/full_node/weight_proof.py` executes a path where make `validate_weight_proof_single_proc` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/weight_proof.py:572 `WeightProofHandler.validate_weight_proof_single_proc`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `validate_weight_proof_single_proc` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/full_node/weight_proof.py:validate_weight_proof_single_proc` and assert both derive the same rejection
