# Q1385: new_tx_block carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_tx_block` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `Mempool.new_tx_block` in `chia/full_node/mempool.py` executes a path where make `new_tx_block` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/mempool.py:329 `Mempool.new_tx_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_tx_block`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `new_tx_block` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/full_node/mempool.py:new_tx_block` and assert stale spend state is purged before replayed data is reconsidered
