# Q1810: generate_launcher_spend normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `generate_launcher_spend` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `PoolWallet.generate_launcher_spend` in `chia/pools/pool_wallet.py` executes a path where make `generate_launcher_spend` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/pools/pool_wallet.py:545 `PoolWallet.generate_launcher_spend`
- Entrypoint: pool wallet or singleton spend flow reaching `generate_launcher_spend`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `generate_launcher_spend` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/pools/pool_wallet.py:generate_launcher_spend` and assert cache/dedup keys separate them correctly
