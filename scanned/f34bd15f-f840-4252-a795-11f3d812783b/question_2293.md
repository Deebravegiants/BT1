# Q2293: create_update_spend carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_update_spend` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `DIDWallet.create_update_spend` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `create_update_spend` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:562 `DIDWallet.create_update_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_update_spend`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `create_update_spend` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/did_wallet/did_wallet.py:create_update_spend` and assert stale spend state is purged before replayed data is reconsidered
