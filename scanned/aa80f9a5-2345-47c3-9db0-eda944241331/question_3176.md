# Q3176: remove_coin carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_coin` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `VCWallet.remove_coin` in `chia/wallet/vc_wallet/vc_wallet.py` executes a path where make `remove_coin` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/vc_wallet.py:130 `VCWallet.remove_coin`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_coin`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `remove_coin` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/vc_wallet/vc_wallet.py:remove_coin` and assert stale spend state is purged before replayed data is reconsidered
