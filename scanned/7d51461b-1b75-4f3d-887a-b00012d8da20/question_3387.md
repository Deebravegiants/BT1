# Q3387: delete_nft_by_coin_id carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `delete_nft_by_coin_id` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `WalletNftStore.delete_nft_by_coin_id` in `chia/wallet/wallet_nft_store.py` executes a path where make `delete_nft_by_coin_id` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_nft_store.py:88 `WalletNftStore.delete_nft_by_coin_id`
- Entrypoint: wallet RPC or wallet sync flow reaching `delete_nft_by_coin_id`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `delete_nft_by_coin_id` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/wallet_nft_store.py:delete_nft_by_coin_id` and assert stale spend state is purged before replayed data is reconsidered
