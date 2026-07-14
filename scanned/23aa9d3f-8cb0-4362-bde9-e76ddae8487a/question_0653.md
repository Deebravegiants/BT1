# Q653: connect_to_solver trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach RPC route `connect_to_solver` and control signage-point, partial-proof, or solver-response contents and timing so that `FarmerRpcApi.connect_to_solver` in `chia/farmer/farmer_rpc_api.py` executes a path where make `connect_to_solver` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/farmer/farmer_rpc_api.py:372 `FarmerRpcApi.connect_to_solver`
- Entrypoint: RPC route `connect_to_solver`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `connect_to_solver` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/farmer/farmer_rpc_api.py:connect_to_solver` and assert current-session state rejects it deterministically
