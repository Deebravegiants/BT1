# Q2240: create_mirror_puzzle carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_mirror_puzzle` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `create_mirror_puzzle` in `chia/wallet/db_wallet/db_wallet_puzzles.py` executes a path where make `create_mirror_puzzle` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/db_wallet/db_wallet_puzzles.py:90 `create_mirror_puzzle`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_mirror_puzzle`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `create_mirror_puzzle` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/db_wallet/db_wallet_puzzles.py:create_mirror_puzzle` and assert stale spend state is purged before replayed data is reconsidered
