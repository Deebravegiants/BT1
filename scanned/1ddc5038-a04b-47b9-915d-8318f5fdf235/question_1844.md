# Q1844: coin_added carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `coin_added` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `PoolWallet.coin_added` in `chia/pools/pool_wallet.py` executes a path where make `coin_added` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/pools/pool_wallet.py:881 `PoolWallet.coin_added`
- Entrypoint: pool wallet or singleton spend flow reaching `coin_added`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `coin_added` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/pools/pool_wallet.py:coin_added` and assert stale spend state is purged before replayed data is reconsidered
