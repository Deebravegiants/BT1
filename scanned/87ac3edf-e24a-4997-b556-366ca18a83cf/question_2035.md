# Q2035: farm_block reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach RPC route `farm_block` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `SimulatorFullNodeRpcApi.farm_block` in `chia/simulator/simulator_full_node_rpc_api.py` executes a path where reuse cache, dedup, or seen-set assumptions in `farm_block` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/simulator/simulator_full_node_rpc_api.py:37 `SimulatorFullNodeRpcApi.farm_block`
- Entrypoint: RPC route `farm_block`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `farm_block` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/simulator/simulator_full_node_rpc_api.py:farm_block` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
