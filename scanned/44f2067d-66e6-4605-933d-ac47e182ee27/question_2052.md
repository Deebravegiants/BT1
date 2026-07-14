# Q2052: new_peak_timelord lets plot sync state suppress honest farming actions

## Question
Can an unprivileged attacker reach P2P message handler `new_peak_timelord` and control plot-sync deltas, stale plot lists, and peer identity reuse so that `TimelordAPI.new_peak_timelord` in `chia/timelord/timelord_api.py` executes a path where make `new_peak_timelord` suppress or misapply honest plot state using attacker-driven sync deltas, violating the invariant that plot sync state must not suppress honest plots or stall valid farming actions for long periods and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/timelord/timelord_api.py:60 `TimelordAPI.new_peak_timelord`
- Entrypoint: P2P message handler `new_peak_timelord`
- Attacker controls: plot-sync deltas, stale plot lists, and peer identity reuse
- Exploit idea: make `new_peak_timelord` suppress or misapply honest plot state using attacker-driven sync deltas
- Invariant to test: plot sync state must not suppress honest plots or stall valid farming actions for long periods
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: reorder plot-sync deltas into `chia/timelord/timelord_api.py:new_peak_timelord` and assert honest plots remain visible and actionable
