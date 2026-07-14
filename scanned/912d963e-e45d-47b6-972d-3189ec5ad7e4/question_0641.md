# Q641: get_signage_points trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach RPC route `get_signage_points` and control signage-point, partial-proof, or solver-response contents and timing so that `FarmerRpcApi.get_signage_points` in `chia/farmer/farmer_rpc_api.py` executes a path where make `get_signage_points` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/farmer/farmer_rpc_api.py:266 `FarmerRpcApi.get_signage_points`
- Entrypoint: RPC route `get_signage_points`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `get_signage_points` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/farmer/farmer_rpc_api.py:get_signage_points` and assert current-session state rejects it deterministically
