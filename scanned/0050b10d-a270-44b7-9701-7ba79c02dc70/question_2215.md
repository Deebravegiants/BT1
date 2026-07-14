# Q2215: select_smallest_coin_over_target carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `select_smallest_coin_over_target` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `select_smallest_coin_over_target` in `chia/wallet/coin_selection.py` executes a path where make `select_smallest_coin_over_target` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/coin_selection.py:131 `select_smallest_coin_over_target`
- Entrypoint: wallet RPC or wallet sync flow reaching `select_smallest_coin_over_target`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `select_smallest_coin_over_target` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/coin_selection.py:select_smallest_coin_over_target` and assert stale spend state is purged before replayed data is reconsidered
