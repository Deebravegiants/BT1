# Q1154: respond_compact_proof_of_time reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach P2P message handler `respond_compact_proof_of_time` and control pending roots, clear/cancel timing, and subsequent root submissions so that `FullNodeAPI.respond_compact_proof_of_time` in `chia/full_node/full_node_api.py` executes a path where make `respond_compact_proof_of_time` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/full_node_api.py:1729 `FullNodeAPI.respond_compact_proof_of_time`
- Entrypoint: P2P message handler `respond_compact_proof_of_time`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `respond_compact_proof_of_time` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/full_node/full_node_api.py:respond_compact_proof_of_time` and assert stale pending roots die cleanly
