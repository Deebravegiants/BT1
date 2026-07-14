# Q1264: get_block_spends_with_conditions mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach RPC route `get_block_spends_with_conditions` and control compact proofs, summarized state, and full-object substitution timing so that `FullNodeRpcApi.get_block_spends_with_conditions` in `chia/full_node/full_node_rpc_api.py` executes a path where swap compact or summarized proof material into `get_block_spends_with_conditions` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:533 `FullNodeRpcApi.get_block_spends_with_conditions`
- Entrypoint: RPC route `get_block_spends_with_conditions`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `get_block_spends_with_conditions` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/full_node/full_node_rpc_api.py:get_block_spends_with_conditions` and assert summarized forms never bypass equivalent validation
