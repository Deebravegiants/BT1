# Q276: submit_all_pending_roots reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach RPC route `submit_all_pending_roots` and control pending roots, clear/cancel timing, and subsequent root submissions so that `DataLayerRpcApi.submit_all_pending_roots` in `chia/data_layer/data_layer_rpc_api.py` executes a path where make `submit_all_pending_roots` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:296 `DataLayerRpcApi.submit_all_pending_roots`
- Entrypoint: RPC route `submit_all_pending_roots`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `submit_all_pending_roots` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/data_layer/data_layer_rpc_api.py:submit_all_pending_roots` and assert stale pending roots die cleanly
