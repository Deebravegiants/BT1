# Q1611: validate_weight_proof reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof` and control pending roots, clear/cancel timing, and subsequent root submissions so that `WeightProofHandler.validate_weight_proof` in `chia/full_node/weight_proof.py` executes a path where make `validate_weight_proof` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/weight_proof.py:605 `WeightProofHandler.validate_weight_proof`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `validate_weight_proof` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/full_node/weight_proof.py:validate_weight_proof` and assert stale pending roots die cleanly
