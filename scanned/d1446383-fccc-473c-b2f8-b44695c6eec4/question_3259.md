# Q3259: new_valid_weight_proof commits or verifies a stale Data Layer root

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_valid_weight_proof` and control store ids, node hashes, roots, and ancestor/proof payloads so that `WalletBlockchain.new_valid_weight_proof` in `chia/wallet/wallet_blockchain.py` executes a path where convince `new_valid_weight_proof` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state, violating the invariant that each Data Layer proof, root, and ancestor chain must bind to exactly one store state and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_blockchain.py:81 `WalletBlockchain.new_valid_weight_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_valid_weight_proof`
- Attacker controls: store ids, node hashes, roots, and ancestor/proof payloads
- Exploit idea: convince `new_valid_weight_proof` to accept a root, proof, or ancestor chain that belongs to the wrong logical store state
- Invariant to test: each Data Layer proof, root, and ancestor chain must bind to exactly one store state
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: feed wrong-store proofs and roots into `chia/wallet/wallet_blockchain.py:new_valid_weight_proof` and assert no root or ancestor verification succeeds cross-store
