# Q48: validate_unfinished_block_header mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach peer-supplied block, proof, or spend path reaching `validate_unfinished_block_header` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `Blockchain.validate_unfinished_block_header` in `chia/consensus/blockchain.py` executes a path where interleave peak changes and rollback-sensitive inputs so `validate_unfinished_block_header` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/consensus/blockchain.py:715 `Blockchain.validate_unfinished_block_header`
- Entrypoint: peer-supplied block, proof, or spend path reaching `validate_unfinished_block_header`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `validate_unfinished_block_header` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/consensus/blockchain.py:validate_unfinished_block_header` with interleaved peaks and assert fork-local state never leaks across rollback
