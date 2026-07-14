# Q1316: create_block_generator derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach RPC route `create_block_generator` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `FullNodeRpcApi.create_block_generator` in `chia/full_node/full_node_rpc_api.py` executes a path where make `create_block_generator` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:967 `FullNodeRpcApi.create_block_generator`
- Entrypoint: RPC route `create_block_generator`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `create_block_generator` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/full_node/full_node_rpc_api.py:create_block_generator` and assert fork choice depends only on canonical validated state
