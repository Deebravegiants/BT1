# Q297: subscribe reuses pending-root state after the security context changed

## Question
Can an unprivileged attacker reach RPC route `subscribe` and control pending roots, clear/cancel timing, and subsequent root submissions so that `DataLayerRpcApi.subscribe` in `chia/data_layer/data_layer_rpc_api.py` executes a path where make `subscribe` reuse pending-root authority after the store's canonical security context changed, violating the invariant that pending-root state must expire when the canonical store security context no longer matches it and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:360 `DataLayerRpcApi.subscribe`
- Entrypoint: RPC route `subscribe`
- Attacker controls: pending roots, clear/cancel timing, and subsequent root submissions
- Exploit idea: make `subscribe` reuse pending-root authority after the store's canonical security context changed
- Invariant to test: pending-root state must expire when the canonical store security context no longer matches it
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: mutate canonical store context between pending-root creation and submit in `chia/data_layer/data_layer_rpc_api.py:subscribe` and assert stale pending roots die cleanly
