# Q649: set_payout_instructions trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach RPC route `set_payout_instructions` and control signage-point, partial-proof, or solver-response contents and timing so that `FarmerRpcApi.set_payout_instructions` in `chia/farmer/farmer_rpc_api.py` executes a path where make `set_payout_instructions` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/farmer/farmer_rpc_api.py:317 `FarmerRpcApi.set_payout_instructions`
- Entrypoint: RPC route `set_payout_instructions`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `set_payout_instructions` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/farmer/farmer_rpc_api.py:set_payout_instructions` and assert current-session state rejects it deterministically
