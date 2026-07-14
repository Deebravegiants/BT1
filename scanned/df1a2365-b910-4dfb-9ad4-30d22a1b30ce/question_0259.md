# Q259: create_data_store cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach RPC route `create_data_store` and control batched updates across multiple store ids and roots so that `DataLayerRpcApi.create_data_store` in `chia/data_layer/data_layer_rpc_api.py` executes a path where make `create_data_store` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:148 `DataLayerRpcApi.create_data_store`
- Entrypoint: RPC route `create_data_store`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `create_data_store` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/data_layer/data_layer_rpc_api.py:create_data_store` and assert no store commits under the wrong root
