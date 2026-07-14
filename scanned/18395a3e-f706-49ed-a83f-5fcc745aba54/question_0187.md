# Q187: stop_plotting trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `stop_plotting` and control signage-point, partial-proof, or solver-response contents and timing so that `WebSocketServer.stop_plotting` in `chia/daemon/server.py` executes a path where make `stop_plotting` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/daemon/server.py:1227 `WebSocketServer.stop_plotting`
- Entrypoint: daemon WebSocket command path reaching `stop_plotting`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `stop_plotting` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/daemon/server.py:stop_plotting` and assert current-session state rejects it deterministically
