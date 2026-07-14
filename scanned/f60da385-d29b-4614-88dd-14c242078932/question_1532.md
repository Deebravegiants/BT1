# Q1532: add_coin_subscriptions normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_coin_subscriptions` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `PeerSubscriptions.add_coin_subscriptions` in `chia/full_node/subscriptions.py` executes a path where make `add_coin_subscriptions` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/subscriptions.py:121 `PeerSubscriptions.add_coin_subscriptions`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_coin_subscriptions`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `add_coin_subscriptions` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/full_node/subscriptions.py:add_coin_subscriptions` and assert cache/dedup keys separate them correctly
