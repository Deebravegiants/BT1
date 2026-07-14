# Q389: get_proof mishandles compact or summarized proof substitution

## Question
Can an unprivileged attacker reach RPC route `get_proof` and control compact proofs, summarized state, and full-object substitution timing so that `DataLayerRpcApi.get_proof` in `chia/data_layer/data_layer_rpc_api.py` executes a path where swap compact or summarized proof material into `get_proof` so it stands in for a stronger object than intended, violating the invariant that compact or summarized proofs must never stand in for stronger proof objects without equivalent validation and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:559 `DataLayerRpcApi.get_proof`
- Entrypoint: RPC route `get_proof`
- Attacker controls: compact proofs, summarized state, and full-object substitution timing
- Exploit idea: swap compact or summarized proof material into `get_proof` so it stands in for a stronger object than intended
- Invariant to test: compact or summarized proofs must never stand in for stronger proof objects without equivalent validation
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: swap compact versus full proof objects into `chia/data_layer/data_layer_rpc_api.py:get_proof` and assert summarized forms never bypass equivalent validation
