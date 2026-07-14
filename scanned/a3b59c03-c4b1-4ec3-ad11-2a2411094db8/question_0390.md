# Q390: get_proof commits or verifies a stale Data Layer root

## Question
Can an unprivileged attacker reach RPC route `get_proof` and control store ids, node hashes, roots, and ancestor/proof payloads so that `DataLayerRpcApi.get_proof` in `chia/data_layer/data_layer_rpc_api.py` executes a path where convince `get_proof` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state, violating the invariant that each Data Layer proof, root, and ancestor chain must bind to exactly one store state and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:559 `DataLayerRpcApi.get_proof`
- Entrypoint: RPC route `get_proof`
- Attacker controls: store ids, node hashes, roots, and ancestor/proof payloads
- Exploit idea: convince `get_proof` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state
- Invariant to test: each Data Layer proof, root, and ancestor chain must bind to exactly one store state
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: feed wrong-store proofs and roots into `chia/data_layer/data_layer_rpc_api.py:get_proof` and assert no root or ancestor verification succeeds cross-store
