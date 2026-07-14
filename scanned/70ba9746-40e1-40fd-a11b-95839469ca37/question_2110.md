# Q2110: coin_added carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `coin_added` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `CATWallet.coin_added` in `chia/wallet/cat_wallet/cat_wallet.py` executes a path where make `coin_added` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/cat_wallet/cat_wallet.py:359 `CATWallet.coin_added`
- Entrypoint: wallet RPC or wallet sync flow reaching `coin_added`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `coin_added` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/cat_wallet/cat_wallet.py:coin_added` and assert stale spend state is purged before replayed data is reconsidered
