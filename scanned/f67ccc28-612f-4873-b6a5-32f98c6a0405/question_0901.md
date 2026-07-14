# Q901: add_to_bad_peak_cache mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_to_bad_peak_cache` and control compact proofs, summarized state, and full-object substitution timing so that `FullNode.add_to_bad_peak_cache` in `chia/full_node/full_node.py` executes a path where swap compact or summarized proof material into `add_to_bad_peak_cache` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node.py:3357 `FullNode.add_to_bad_peak_cache`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_to_bad_peak_cache`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `add_to_bad_peak_cache` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/full_node.py:add_to_bad_peak_cache` and assert summarized forms never bypass equivalent validation
