# Q1647: add_plot_directory lets plot sync state suppress honest farming actions

## Question
Can an unprivileged attacker reach RPC route `add_plot_directory` and control plot-sync deltas, stale plot lists, and peer identity reuse so that `HarvesterRpcApi.add_plot_directory` in `chia/harvester/harvester_rpc_api.py` executes a path where make `add_plot_directory` suppress or misapply honest plot state using attacker-driven sync deltas, violating the invariant that plot sync state must not suppress honest plots or stall valid farming actions for long periods and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/harvester/harvester_rpc_api.py:75 `HarvesterRpcApi.add_plot_directory`
- Entrypoint: RPC route `add_plot_directory`
- Attacker controls: plot-sync deltas, stale plot lists, and peer identity reuse
- Exploit idea: make `add_plot_directory` suppress or misapply honest plot state using attacker-driven sync deltas
- Invariant to test: plot sync state must not suppress honest plots or stall valid farming actions for long periods
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: reorder plot-sync deltas into `chia/harvester/harvester_rpc_api.py:add_plot_directory` and assert honest plots remain visible and actionable
