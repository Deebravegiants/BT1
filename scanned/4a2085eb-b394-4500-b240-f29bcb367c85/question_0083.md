# Q83: add_block_record mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `add_block_record` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `BlocksProtocol.add_block_record` in `chia/consensus/blockchain_interface.py` executes a path where interleave peak changes and rollback-sensitive inputs so `add_block_record` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/blockchain_interface.py:52 `BlocksProtocol.add_block_record`
- Entrypoint: peer-supplied block, proof, or spend path reaching `add_block_record`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `add_block_record` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/consensus/blockchain_interface.py:add_block_record` with interleaved peaks and assert fork-local state never leaks across rollback
