# Q403: verify_proof redirects or misbinds Data Layer mirror state

## Question
Can an unprivileged attacker reach RPC route `verify_proof` and control mirror identifiers, store ids, urls, payout-linked state, and pending-root timing so that `DataLayerRpcApi.verify_proof` in `chia/data_layer/data_layer_rpc_api.py` executes a path where make `verify_proof` apply mirror-linked state changes to a different store, payout target, or pending-root context, violating the invariant that mirror state changes must bind to the intended store and payout-linked singleton state only and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:597 `DataLayerRpcApi.verify_proof`
- Entrypoint: RPC route `verify_proof`
- Attacker controls: mirror identifiers, store ids, urls, payout-linked state, and pending-root timing
- Exploit idea: make `verify_proof` apply mirror-linked state changes to a different store, payout target, or pending-root context
- Invariant to test: mirror state changes must bind to the intended store and payout-linked singleton state only
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: exercise add/delete mirror flows around pending-root changes and assert `chia/data_layer/data_layer_rpc_api.py:verify_proof` binds every effect to the intended store
