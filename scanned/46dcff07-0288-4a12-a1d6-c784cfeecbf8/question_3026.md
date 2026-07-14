# Q3026: request_header_blocks mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `request_header_blocks` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `request_header_blocks` in `chia/wallet/util/wallet_sync_utils.py` executes a path where interleave peak changes and rollback-sensitive inputs so `request_header_blocks` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/wallet_sync_utils.py:248 `request_header_blocks`
- Entrypoint: wallet RPC or wallet sync flow reaching `request_header_blocks`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `request_header_blocks` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/util/wallet_sync_utils.py:request_header_blocks` with interleaved peaks and assert fork-local state never leaks across rollback
