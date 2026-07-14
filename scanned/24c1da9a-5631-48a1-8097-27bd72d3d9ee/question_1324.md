# Q1324: remove_requesting_unfinished_block mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_requesting_unfinished_block` and control compact proofs, summarized state, and full-object substitution timing so that `FullNodeStore.remove_requesting_unfinished_block` in `chia/full_node/full_node_store.py` executes a path where swap compact or summarized proof material into `remove_requesting_unfinished_block` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_store.py:225 `FullNodeStore.remove_requesting_unfinished_block`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_requesting_unfinished_block`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `remove_requesting_unfinished_block` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/full_node_store.py:remove_requesting_unfinished_block` and assert summarized forms never bypass equivalent validation
