# Q321: add_mirror cross-contaminates multiple Data Layer stores

## Question
Can an unprivileged attacker reach RPC route `add_mirror` and control batched updates across multiple store ids and roots so that `DataLayerRpcApi.add_mirror` in `chia/data_layer/data_layer_rpc_api.py` executes a path where make `add_mirror` commit part of a multi-store update under the wrong root or wrong store id, violating the invariant that batched Data Layer updates must be atomic per stated store set and root set and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:468 `DataLayerRpcApi.add_mirror`
- Entrypoint: RPC route `add_mirror`
- Attacker controls: batched updates across multiple store ids and roots
- Exploit idea: make `add_mirror` commit part of a multi-store update under the wrong root or wrong store id
- Invariant to test: batched Data Layer updates must be atomic per stated store set and root set
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: inject a partial-failure batched update into `chia/data_layer/data_layer_rpc_api.py:add_mirror` and assert no store commits under the wrong root
