# Q2954: subscribe_to_coin_ids normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `NewPeakQueue.subscribe_to_coin_ids` in `chia/wallet/util/new_peak_queue.py` executes a path where make `subscribe_to_coin_ids` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/util/new_peak_queue.py:61 `NewPeakQueue.subscribe_to_coin_ids`
- Entrypoint: wallet RPC or wallet sync flow reaching `subscribe_to_coin_ids`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `subscribe_to_coin_ids` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/wallet/util/new_peak_queue.py:subscribe_to_coin_ids` and assert cache/dedup keys separate them correctly
