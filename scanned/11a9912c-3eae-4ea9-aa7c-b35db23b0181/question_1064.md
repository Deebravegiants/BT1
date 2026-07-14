# Q1064: declare_proof_of_space reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach P2P message handler `declare_proof_of_space` and control pending roots, clear/cancel timing, and subsequent root submissions so that `FullNodeAPI.declare_proof_of_space` in `chia/full_node/full_node_api.py` executes a path where make `declare_proof_of_space` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:892 `FullNodeAPI.declare_proof_of_space`
- Entrypoint: P2P message handler `declare_proof_of_space`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `declare_proof_of_space` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/full_node/full_node_api.py:declare_proof_of_space` and assert stale pending roots die cleanly
