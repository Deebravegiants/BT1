# Q688: remove_mempool_item carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_mempool_item` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `BitcoinFeeEstimator.remove_mempool_item` in `chia/full_node/bitcoin_fee_estimator.py` executes a path where make `remove_mempool_item` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/bitcoin_fee_estimator.py:42 `BitcoinFeeEstimator.remove_mempool_item`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_mempool_item`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `remove_mempool_item` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/full_node/bitcoin_fee_estimator.py:remove_mempool_item` and assert stale spend state is purged before replayed data is reconsidered
