# Q946: request_proof_of_weight reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach P2P message handler `request_proof_of_weight` and control pending roots, clear/cancel timing, and subsequent root submissions so that `FullNodeAPI.request_proof_of_weight` in `chia/full_node/full_node_api.py` executes a path where make `request_proof_of_weight` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:360 `FullNodeAPI.request_proof_of_weight`
- Entrypoint: P2P message handler `request_proof_of_weight`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `request_proof_of_weight` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/full_node/full_node_api.py:request_proof_of_weight` and assert stale pending roots die cleanly
