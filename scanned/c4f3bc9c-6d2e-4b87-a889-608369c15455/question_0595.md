# Q595: partial_proofs lets plot sync state suppress honest farming actions

## Question
Can an unprivileged attacker reach P2P message handler `partial_proofs` and control plot-sync deltas, stale plot lists, and peer identity reuse so that `FarmerAPI.partial_proofs` in `chia/farmer/farmer_api.py` executes a path where make `partial_proofs` suppress or misapply honest plot state using attacker-driven sync deltas, violating the invariant that plot sync state must not suppress honest plots or stall valid farming actions for long periods and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/farmer/farmer_api.py:495 `FarmerAPI.partial_proofs`
- Entrypoint: P2P message handler `partial_proofs`
- Attacker controls: plot-sync deltas, stale plot lists, and peer identity reuse
- Exploit idea: make `partial_proofs` suppress or misapply honest plot state using attacker-driven sync deltas
- Invariant to test: plot sync state must not suppress honest plots or stall valid farming actions for long periods
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: reorder plot-sync deltas into `chia/farmer/farmer_api.py:partial_proofs` and assert honest plots remain visible and actionable
