# Q2478: update_coin_status carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `update_coin_status` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `NFTWallet.update_coin_status` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `update_coin_status` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:482 `NFTWallet.update_coin_status`
- Entrypoint: wallet RPC or wallet sync flow reaching `update_coin_status`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `update_coin_status` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/nft_wallet/nft_wallet.py:update_coin_status` and assert stale spend state is purged before replayed data is reconsidered
