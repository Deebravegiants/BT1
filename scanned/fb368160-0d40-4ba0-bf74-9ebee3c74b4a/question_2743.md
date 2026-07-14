# Q2743: generate_m_of_n_proof redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_m_of_n_proof` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `MofNMerkleTree.generate_m_of_n_proof` in `chia/wallet/puzzles/custody/custody_architecture.py` executes a path where make `generate_m_of_n_proof` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/puzzles/custody/custody_architecture.py:143 `MofNMerkleTree.generate_m_of_n_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_m_of_n_proof`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `generate_m_of_n_proof` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/wallet/puzzles/custody/custody_architecture.py:generate_m_of_n_proof` binds every effect to the intended store
