# Q1740: create_p2_singleton_puzzle normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `create_p2_singleton_puzzle` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `create_p2_singleton_puzzle` in `chia/pools/pool_puzzles.py` executes a path where make `create_p2_singleton_puzzle` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/pools/pool_puzzles.py:91 `create_p2_singleton_puzzle`
- Entrypoint: pool wallet or singleton spend flow reaching `create_p2_singleton_puzzle`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `create_p2_singleton_puzzle` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/pools/pool_puzzles.py:create_p2_singleton_puzzle` and assert cache/dedup keys separate them correctly
