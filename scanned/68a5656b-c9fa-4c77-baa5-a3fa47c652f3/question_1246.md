# Q1246: get_block_spends mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach RPC route `get_block_spends` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `FullNodeRpcApi.get_block_spends` in `chia/full_node/full_node_rpc_api.py` executes a path where interleave peak changes and rollback-sensitive inputs so `get_block_spends` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:502 `FullNodeRpcApi.get_block_spends`
- Entrypoint: RPC route `get_block_spends`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `get_block_spends` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/full_node/full_node_rpc_api.py:get_block_spends` with interleaved peaks and assert fork-local state never leaks across rollback
