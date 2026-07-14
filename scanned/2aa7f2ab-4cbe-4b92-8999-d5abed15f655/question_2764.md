# Q2764: make_assert_coin_announcement carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `make_assert_coin_announcement` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `make_assert_coin_announcement` in `chia/wallet/puzzles/puzzle_utils.py` executes a path where make `make_assert_coin_announcement` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/puzzles/puzzle_utils.py:22 `make_assert_coin_announcement`
- Entrypoint: wallet RPC or wallet sync flow reaching `make_assert_coin_announcement`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `make_assert_coin_announcement` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/puzzles/puzzle_utils.py:make_assert_coin_announcement` and assert stale spend state is purged before replayed data is reconsidered
