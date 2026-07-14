# Q3142: add_vc_proofs mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_vc_proofs` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `VCStore.add_vc_proofs` in `chia/wallet/vc_wallet/vc_store.py` executes a path where interleave peak changes and rollback-sensitive inputs so `add_vc_proofs` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/vc_wallet/vc_store.py:246 `VCStore.add_vc_proofs`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_vc_proofs`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `add_vc_proofs` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/vc_wallet/vc_store.py:add_vc_proofs` with interleaved peaks and assert fork-local state never leaks across rollback
