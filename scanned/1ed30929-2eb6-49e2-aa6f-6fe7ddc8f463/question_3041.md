# Q3041: spend_many carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `spend_many` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `CRCAT.spend_many` in `chia/wallet/vc_wallet/cr_cat_drivers.py` executes a path where make `spend_many` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_drivers.py:515 `CRCAT.spend_many`
- Entrypoint: wallet RPC or wallet sync flow reaching `spend_many`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `spend_many` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/vc_wallet/cr_cat_drivers.py:spend_many` and assert stale spend state is purged before replayed data is reconsidered
