# Q188: stop_plotting lets plot sync state suppress honest farming actions

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `stop_plotting` and control plot-sync deltas, stale plot lists, and peer identity reuse so that `WebSocketServer.stop_plotting` in `chia/daemon/server.py` executes a path where make `stop_plotting` suppress or misapply honest plot state using attacker-driven sync deltas, violating the invariant that plot sync state must not suppress honest plots or stall valid farming actions for long periods and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/daemon/server.py:1227 `WebSocketServer.stop_plotting`
- Entrypoint: daemon WebSocket command path reaching `stop_plotting`
- Attacker controls: plot-sync deltas, stale plot lists, and peer identity reuse
- Exploit idea: make `stop_plotting` suppress or misapply honest plot state using attacker-driven sync deltas
- Invariant to test: plot sync state must not suppress honest plots or stall valid farming actions for long periods
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: reorder plot-sync deltas into `chia/daemon/server.py:stop_plotting` and assert honest plots remain visible and actionable
