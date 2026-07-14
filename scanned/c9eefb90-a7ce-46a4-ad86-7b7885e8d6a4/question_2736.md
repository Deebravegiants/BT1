# Q2736: generate_m_of_n_proof mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_m_of_n_proof` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `MofNMerkleTree.generate_m_of_n_proof` in `chia/wallet/puzzles/custody/custody_architecture.py` executes a path where interleave peak changes and rollback-sensitive inputs so `generate_m_of_n_proof` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/puzzles/custody/custody_architecture.py:143 `MofNMerkleTree.generate_m_of_n_proof`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_m_of_n_proof`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `generate_m_of_n_proof` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/wallet/puzzles/custody/custody_architecture.py:generate_m_of_n_proof` with interleaved peaks and assert fork-local state never leaks across rollback
