# Q2936: generate_proof redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_proof` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `MerkleTree.generate_proof` in `chia/wallet/util/merkle_tree.py` executes a path where make `generate_proof` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/util/merkle_tree.py:97 `MerkleTree.generate_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_proof`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `generate_proof` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/wallet/util/merkle_tree.py:generate_proof` binds every effect to the intended store
