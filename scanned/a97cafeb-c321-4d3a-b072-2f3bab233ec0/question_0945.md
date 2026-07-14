# Q945: request_proof_of_weight redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach P2P message handler `request_proof_of_weight` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `FullNodeAPI.request_proof_of_weight` in `chia/full_node/full_node_api.py` executes a path where make `request_proof_of_weight` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:360 `FullNodeAPI.request_proof_of_weight`
- Entrypoint: P2P message handler `request_proof_of_weight`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `request_proof_of_weight` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/full_node/full_node_api.py:request_proof_of_weight` binds every effect to the intended store
