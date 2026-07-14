# Q388: get_proof derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach RPC route `get_proof` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `DataLayerRpcApi.get_proof` in `chia/data_layer/data_layer_rpc_api.py` executes a path where make `get_proof` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/data_layer/data_layer_rpc_api.py:559 `DataLayerRpcApi.get_proof`
- Entrypoint: RPC route `get_proof`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `get_proof` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/data_layer/data_layer_rpc_api.py:get_proof` and assert fork choice depends only on canonical validated state
