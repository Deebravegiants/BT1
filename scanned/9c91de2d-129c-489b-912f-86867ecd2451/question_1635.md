# Q1635: request_signatures lets plot sync state suppress honest farming actions

## Question
Can an unprivileged attacker reach P2P message handler `request_signatures` and control plot-sync deltas, stale plot lists, and peer identity reuse so that `HarvesterAPI.request_signatures` in `chia/harvester/harvester_api.py` executes a path where make `request_signatures` suppress or misapply honest plot state using attacker-driven sync deltas, violating the invariant that plot sync state must not suppress honest plots or stall valid farming actions for long periods and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/harvester/harvester_api.py:478 `HarvesterAPI.request_signatures`
- Entrypoint: P2P message handler `request_signatures`
- Attacker controls: plot-sync deltas, stale plot lists, and peer identity reuse
- Exploit idea: make `request_signatures` suppress or misapply honest plot state using attacker-driven sync deltas
- Invariant to test: plot sync state must not suppress honest plots or stall valid farming actions for long periods
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: reorder plot-sync deltas into `chia/harvester/harvester_api.py:request_signatures` and assert honest plots remain visible and actionable
