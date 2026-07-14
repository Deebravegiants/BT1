# Q2041: set_auto_farming lets plot sync state suppress honest farming actions

## Question
Can an unprivileged attacker reach RPC route `set_auto_farming` and control plot-sync deltas, stale plot lists, and peer identity reuse so that `SimulatorFullNodeRpcApi.set_auto_farming` in `chia/simulator/simulator_full_node_rpc_api.py` executes a path where make `set_auto_farming` suppress or misapply honest plot state using attacker-driven sync deltas, violating the invariant that plot sync state must not suppress honest plots or stall valid farming actions for long periods and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/simulator/simulator_full_node_rpc_api.py:52 `SimulatorFullNodeRpcApi.set_auto_farming`
- Entrypoint: RPC route `set_auto_farming`
- Attacker controls: plot-sync deltas, stale plot lists, and peer identity reuse
- Exploit idea: make `set_auto_farming` suppress or misapply honest plot state using attacker-driven sync deltas
- Invariant to test: plot sync state must not suppress honest plots or stall valid farming actions for long periods
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: reorder plot-sync deltas into `chia/simulator/simulator_full_node_rpc_api.py:set_auto_farming` and assert honest plots remain visible and actionable
