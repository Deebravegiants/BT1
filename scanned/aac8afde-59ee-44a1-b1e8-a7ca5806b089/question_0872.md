# Q872: add_compact_proof_of_time redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_compact_proof_of_time` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `FullNode.add_compact_proof_of_time` in `chia/full_node/full_node.py` executes a path where make `add_compact_proof_of_time` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node.py:3241 `FullNode.add_compact_proof_of_time`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_compact_proof_of_time`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `add_compact_proof_of_time` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/full_node/full_node.py:add_compact_proof_of_time` binds every effect to the intended store
