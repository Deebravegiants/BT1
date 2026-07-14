# Q3213: select_coins carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `select_coins` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `VCWallet.select_coins` in `chia/wallet/vc_wallet/vc_wallet.py` executes a path where make `select_coins` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/vc_wallet.py:593 `VCWallet.select_coins`
- Entrypoint: wallet RPC or wallet sync flow reaching `select_coins`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `select_coins` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/vc_wallet/vc_wallet.py:select_coins` and assert stale spend state is purged before replayed data is reconsidered
