# Q3494: new_peak_wallet mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach P2P message handler `new_peak_wallet` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `WalletNodeAPI.new_peak_wallet` in `chia/wallet/wallet_node_api.py` executes a path where interleave peak changes and rollback-sensitive inputs so `new_peak_wallet` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node_api.py:53 `WalletNodeAPI.new_peak_wallet`
- Entrypoint: P2P message handler `new_peak_wallet`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `new_peak_wallet` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/wallet_node_api.py:new_peak_wallet` with interleaved peaks and assert fork-local state never leaks across rollback
