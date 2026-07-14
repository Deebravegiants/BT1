# Q1801: generate_fee_transaction carries spend state across rollback boundaries

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `generate_fee_transaction` and control rollback timing, reorg ordering, and stale mempool or wallet state so that `PoolWallet.generate_fee_transaction` in `chia/pools/pool_wallet.py` executes a path where make `generate_fee_transaction` keep attacker-shaped spend state alive across rollback or reorg cleanup, violating the invariant that rollback must remove invalidated spend state completely before any replayed inputs are reconsidered and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/pools/pool_wallet.py:445 `PoolWallet.generate_fee_transaction`
- Entrypoint: pool wallet or singleton spend flow reaching `generate_fee_transaction`
- Attacker controls: rollback timing, reorg ordering, and stale mempool or wallet state
- Exploit idea: make `generate_fee_transaction` keep attacker-shaped spend state alive across rollback or reorg cleanup
- Invariant to test: rollback must remove invalidated spend state completely before any replayed inputs are reconsidered
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: force rollback around `chia/pools/pool_wallet.py:generate_fee_transaction` and assert stale spend state is purged before replayed data is reconsidered
