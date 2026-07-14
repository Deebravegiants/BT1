# Q3767: get_coin_records_by_names normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach RPC route `get_coin_records_by_names` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `WalletRpcApi.get_coin_records_by_names` in `chia/wallet/wallet_rpc_api.py` executes a path where make `get_coin_records_by_names` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1753 `WalletRpcApi.get_coin_records_by_names`
- Entrypoint: RPC route `get_coin_records_by_names`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `get_coin_records_by_names` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/wallet/wallet_rpc_api.py:get_coin_records_by_names` and assert cache/dedup keys separate them correctly
