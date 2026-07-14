# Q3601: respond_blocks mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach P2P message handler `respond_blocks` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `WalletNodeAPI.respond_blocks` in `chia/wallet/wallet_node_api.py` executes a path where interleave peak changes and rollback-sensitive inputs so `respond_blocks` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_node_api.py:220 `WalletNodeAPI.respond_blocks`
- Entrypoint: P2P message handler `respond_blocks`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `respond_blocks` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/wallet_node_api.py:respond_blocks` with interleaved peaks and assert fork-local state never leaks across rollback
