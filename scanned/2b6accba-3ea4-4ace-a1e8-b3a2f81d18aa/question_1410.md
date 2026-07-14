# Q1410: update_spend_index carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `update_spend_index` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `Mempool.update_spend_index` in `chia/full_node/mempool.py` executes a path where make `update_spend_index` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/mempool.py:505 `Mempool.update_spend_index`
- Entrypoint: full node mempool, sync, or peer flow reaching `update_spend_index`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `update_spend_index` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/full_node/mempool.py:update_spend_index` and assert stale spend state is purged before replayed data is reconsidered
