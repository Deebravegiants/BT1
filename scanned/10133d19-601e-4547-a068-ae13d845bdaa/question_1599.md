# Q1599: validate_weight_proof_single_proc redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `WeightProofHandler.validate_weight_proof_single_proc` in `chia/full_node/weight_proof.py` executes a path where make `validate_weight_proof_single_proc` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/weight_proof.py:572 `WeightProofHandler.validate_weight_proof_single_proc`
- Entrypoint: full node mempool, sync, or peer flow reaching `validate_weight_proof_single_proc`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `validate_weight_proof_single_proc` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/full_node/weight_proof.py:validate_weight_proof_single_proc` binds every effect to the intended store
