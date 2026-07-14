# Q3232: generate_signed_transaction carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_signed_transaction` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `Wallet.generate_signed_transaction` in `chia/wallet/wallet.py` executes a path where make `generate_signed_transaction` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet.py:369 `Wallet.generate_signed_transaction`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_signed_transaction`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `generate_signed_transaction` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/wallet/wallet.py:generate_signed_transaction` and assert stale spend state is purged before replayed data is reconsidered
