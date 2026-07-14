# Q1598: validate_weight_proof_single_proc cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc` and control batched updates across multiple store ids and roots so that `WeightProofHandler.validate_weight_proof_single_proc` in `chia/full_node/weight_proof.py` executes a path where make `validate_weight_proof_single_proc` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/weight_proof.py:572 `WeightProofHandler.validate_weight_proof_single_proc`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `validate_weight_proof_single_proc` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/full_node/weight_proof.py:validate_weight_proof_single_proc` and assert no store commits under the wrong root
