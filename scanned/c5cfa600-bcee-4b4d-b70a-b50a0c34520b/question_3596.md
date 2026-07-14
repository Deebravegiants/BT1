# Q3596: respond_fee_estimates stores attacker-driven wallet state that survives rollback

## Question
Can an unprivileged attacker reach P2P message handler `respond_fee_estimates` and control coin states, hints, lineage, and reorg ordering delivered to wallet sync code so that `WalletNodeAPI.respond_fee_estimates` in `chia/wallet/wallet_node_api.py` executes a path where make `respond_fee_estimates` persist wallet state that remains after rollback even though the underlying chain state changed, violating the invariant that wallet persistent state must remain a faithful projection of canonical chain state across reorgs and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_node_api.py:216 `WalletNodeAPI.respond_fee_estimates`
- Entrypoint: P2P message handler `respond_fee_estimates`
- Attacker controls: coin states, hints, lineage, and reorg ordering delivered to wallet sync code
- Exploit idea: make `respond_fee_estimates` persist wallet state that remains after rollback even though the underlying chain state changed
- Invariant to test: wallet persistent state must remain a faithful projection of canonical chain state across reorgs
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: run a wallet reorg harness through `chia/wallet/wallet_node_api.py:respond_fee_estimates` and assert persisted records exactly track canonical chain state
