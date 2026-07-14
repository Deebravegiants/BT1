# Q728: batch_coin_states_by_puzzle_hashes carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `batch_coin_states_by_puzzle_hashes` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `CoinStore.batch_coin_states_by_puzzle_hashes` in `chia/full_node/coin_store.py` executes a path where make `batch_coin_states_by_puzzle_hashes` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/full_node/coin_store.py:451 `CoinStore.batch_coin_states_by_puzzle_hashes`
- Entrypoint: full node mempool, sync, or peer flow reaching `batch_coin_states_by_puzzle_hashes`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `batch_coin_states_by_puzzle_hashes` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/full_node/coin_store.py:batch_coin_states_by_puzzle_hashes` and assert stale spend state is purged before replayed data is reconsidered
