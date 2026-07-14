# Q471: new_peak commits or verifies a stale Data Layer root

## Question
Can an unprivileged attacker reach Data Layer wallet, sync, or store flow reaching `new_peak` and control store ids, node hashes, roots, and ancestor/proof payloads so that `DataLayerWallet.new_peak` in `chia/data_layer/data_layer_wallet.py` executes a path where convince `new_peak` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state, violating the invariant that each Data Layer proof, root, and ancestor chain must bind to exactly one store state and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/data_layer/data_layer_wallet.py:952 `DataLayerWallet.new_peak`
- Entrypoint: Data Layer wallet, sync, or store flow reaching `new_peak`
- Attacker controls: store ids, node hashes, roots, and ancestor/proof payloads
- Exploit idea: convince `new_peak` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state
- Invariant to test: each Data Layer proof, root, and ancestor chain must bind to exactly one store state
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: feed wrong-store proofs and roots into `chia/data_layer/data_layer_wallet.py:new_peak` and assert no root or ancestor verification succeeds cross-store
