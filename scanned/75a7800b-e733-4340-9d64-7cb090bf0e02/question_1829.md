# Q1829: new_peak mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `new_peak` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `PoolWallet.new_peak` in `chia/pools/pool_wallet.py` executes a path where interleave peak changes and rollback-sensitive inputs so `new_peak` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/pools/pool_wallet.py:807 `PoolWallet.new_peak`
- Entrypoint: pool wallet or singleton spend flow reaching `new_peak`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `new_peak` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/pools/pool_wallet.py:new_peak` with interleaved peaks and assert fork-local state never leaks across rollback
