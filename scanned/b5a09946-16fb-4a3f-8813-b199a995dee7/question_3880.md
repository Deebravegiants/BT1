# Q3880: delete_singleton_by_coin_id normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `delete_singleton_by_coin_id` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `WalletSingletonStore.delete_singleton_by_coin_id` in `chia/wallet/wallet_singleton_store.py` executes a path where make `delete_singleton_by_coin_id` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_singleton_store.py:159 `WalletSingletonStore.delete_singleton_by_coin_id`
- Entrypoint: wallet RPC or wallet sync flow reaching `delete_singleton_by_coin_id`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `delete_singleton_by_coin_id` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/wallet/wallet_singleton_store.py:delete_singleton_by_coin_id` and assert cache/dedup keys separate them correctly
