# Q3583: respond_to_coin_updates carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach P2P message handler `respond_to_coin_updates` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `WalletNodeAPI.respond_to_coin_updates` in `chia/wallet/wallet_node_api.py` executes a path where make `respond_to_coin_updates` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_node_api.py:204 `WalletNodeAPI.respond_to_coin_updates`
- Entrypoint: P2P message handler `respond_to_coin_updates`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `respond_to_coin_updates` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/wallet_node_api.py:respond_to_coin_updates` and assert stale spend state is purged before replayed data is reconsidered
