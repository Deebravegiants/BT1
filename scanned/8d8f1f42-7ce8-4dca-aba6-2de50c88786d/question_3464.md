# Q3464: sync_from_untrusted_close_to_peak mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `WalletNode.sync_from_untrusted_close_to_peak` in `chia/wallet/wallet_node.py` executes a path where interleave peak changes and rollback-sensitive inputs so `sync_from_untrusted_close_to_peak` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node.py:1339 `WalletNode.sync_from_untrusted_close_to_peak`
- Entrypoint: wallet RPC or wallet sync flow reaching `sync_from_untrusted_close_to_peak`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `sync_from_untrusted_close_to_peak` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/wallet_node.py:sync_from_untrusted_close_to_peak` with interleaved peaks and assert fork-local state never leaks across rollback
