# Q3263: new_valid_weight_proof stores attacker-driven wallet state that survives rollback

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_valid_weight_proof` and control coin states, hints, lineage, and reorg ordering delivered to wallet sync code so that `WalletBlockchain.new_valid_weight_proof` in `chia/wallet/wallet_blockchain.py` executes a path where make `new_valid_weight_proof` persist wallet state that remains after rollback even though the underlying chain state changed, violating the invariant that wallet persistent state must remain a faithful projection of canonical chain state across reorgs and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_blockchain.py:81 `WalletBlockchain.new_valid_weight_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_valid_weight_proof`
- Attacker controls: coin states, hints, lineage, and reorg ordering delivered to wallet sync code
- Exploit idea: make `new_valid_weight_proof` persist wallet state that remains after rollback even though the underlying chain state changed
- Invariant to test: wallet persistent state must remain a faithful projection of canonical chain state across reorgs
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: run a wallet reorg harness through `chia/wallet/wallet_blockchain.py:new_valid_weight_proof` and assert persisted records exactly track canonical chain state
