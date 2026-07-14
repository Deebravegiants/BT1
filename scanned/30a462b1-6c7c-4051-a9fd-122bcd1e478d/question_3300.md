# Q3300: add_block_record stores attacker-driven wallet state that survives rollback

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_block_record` and control coin states, hints, lineage, and reorg ordering delivered to wallet sync code so that `WalletBlockchain.add_block_record` in `chia/wallet/wallet_blockchain.py` executes a path where make `add_block_record` persist wallet state that remains after rollback even though the underlying chain state changed, violating the invariant that wallet persistent state must remain a faithful projection of canonical chain state across reorgs and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_blockchain.py:251 `WalletBlockchain.add_block_record`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_block_record`
- Attacker controls: coin states, hints, lineage, and reorg ordering delivered to wallet sync code
- Exploit idea: make `add_block_record` persist wallet state that remains after rollback even though the underlying chain state changed
- Invariant to test: wallet persistent state must remain a faithful projection of canonical chain state across reorgs
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: run a wallet reorg harness through `chia/wallet/wallet_blockchain.py:add_block_record` and assert persisted records exactly track canonical chain state
