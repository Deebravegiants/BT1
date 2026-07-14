# Q2844: add_coin_ids normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_coin_ids` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `RemoteCoinStore.add_coin_ids` in `chia/wallet/remote_wallet/remote_coin_store.py` executes a path where make `add_coin_ids` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/remote_wallet/remote_coin_store.py:27 `RemoteCoinStore.add_coin_ids`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_coin_ids`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `add_coin_ids` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/wallet/remote_wallet/remote_coin_store.py:add_coin_ids` and assert cache/dedup keys separate them correctly
