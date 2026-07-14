# Q393: get_proof reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach RPC route `get_proof` and control pending roots, clear/cancel timing, and subsequent root submissions so that `DataLayerRpcApi.get_proof` in `chia/data_layer/data_layer_rpc_api.py` executes a path where make `get_proof` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:559 `DataLayerRpcApi.get_proof`
- Entrypoint: RPC route `get_proof`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `get_proof` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/data_layer/data_layer_rpc_api.py:get_proof` and assert stale pending roots die cleanly
