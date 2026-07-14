# Q1462: create_block_generator mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `create_block_generator` and control compact proofs, summarized state, and full-object substitution timing so that `MempoolManager.create_block_generator` in `chia/full_node/mempool_manager.py` executes a path where swap compact or summarized proof material into `create_block_generator` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/mempool_manager.py:420 `MempoolManager.create_block_generator`
- Entrypoint: full node mempool, sync, or peer flow reaching `create_block_generator`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `create_block_generator` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/mempool_manager.py:create_block_generator` and assert summarized forms never bypass equivalent validation
