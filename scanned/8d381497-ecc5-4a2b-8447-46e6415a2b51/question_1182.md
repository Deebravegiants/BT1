# Q1182: register_for_coin_updates normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach P2P message handler `register_for_coin_updates` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `FullNodeAPI.register_for_coin_updates` in `chia/full_node/full_node_api.py` executes a path where make `register_for_coin_updates` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_api.py:1890 `FullNodeAPI.register_for_coin_updates`
- Entrypoint: P2P message handler `register_for_coin_updates`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `register_for_coin_updates` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/full_node/full_node_api.py:register_for_coin_updates` and assert cache/dedup keys separate them correctly
