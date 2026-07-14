# Q2363: create_spend_for_message carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_spend_for_message` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `create_spend_for_message` in `chia/wallet/did_wallet/did_wallet_puzzles.py` executes a path where make `create_spend_for_message` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/did_wallet/did_wallet_puzzles.py:157 `create_spend_for_message`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_spend_for_message`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `create_spend_for_message` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/did_wallet/did_wallet_puzzles.py:create_spend_for_message` and assert stale spend state is purged before replayed data is reconsidered
