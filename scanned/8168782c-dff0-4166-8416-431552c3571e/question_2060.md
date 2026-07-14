# Q2060: check_orphaned_unfinished_block mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach P2P message handler `check_orphaned_unfinished_block` and control compact proofs, summarized state, and full-object substitution timing so that `TimelordAPI.check_orphaned_unfinished_block` in `chia/timelord/timelord_api.py` executes a path where swap compact or summarized proof material into `check_orphaned_unfinished_block` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/timelord/timelord_api.py:122 `TimelordAPI.check_orphaned_unfinished_block`
- Entrypoint: P2P message handler `check_orphaned_unfinished_block`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `check_orphaned_unfinished_block` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/timelord/timelord_api.py:check_orphaned_unfinished_block` and assert summarized forms never bypass equivalent validation
