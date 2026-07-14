# Q1294: get_mempool_item_by_tx_id normalizes attacker-controlled spend identity inconsistently

## Question
Can an unprivileged attacker reach RPC route `get_mempool_item_by_tx_id` and control serialized bytes, ids, and normalization-sensitive fields that should identify one spend path so that `FullNodeRpcApi.get_mempool_item_by_tx_id` in `chia/full_node/full_node_rpc_api.py` executes a path where make `get_mempool_item_by_tx_id` treat two materially different spend objects as the same identity or the same object as two identities, violating the invariant that canonical spend identity must be stable across serialization, caching, and dedup boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:941 `FullNodeRpcApi.get_mempool_item_by_tx_id`
- Entrypoint: RPC route `get_mempool_item_by_tx_id`
- Attacker controls: serialized bytes, ids, and normalization-sensitive fields that should identify one spend path
- Exploit idea: make `get_mempool_item_by_tx_id` treat two materially different spend objects as the same identity or the same object as two identities
- Invariant to test: canonical spend identity must be stable across serialization, caching, and dedup boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: serialize semantically distinct inputs into `chia/full_node/full_node_rpc_api.py:get_mempool_item_by_tx_id` and assert cache/dedup keys separate them correctly
