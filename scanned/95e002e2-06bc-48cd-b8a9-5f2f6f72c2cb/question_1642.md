# Q1642: delete_plot trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach RPC route `delete_plot` and control signage-point, partial-proof, or solver-response contents and timing so that `HarvesterRpcApi.delete_plot` in `chia/harvester/harvester_rpc_api.py` executes a path where make `delete_plot` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/harvester/harvester_rpc_api.py:69 `HarvesterRpcApi.delete_plot`
- Entrypoint: RPC route `delete_plot`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `delete_plot` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/harvester/harvester_rpc_api.py:delete_plot` and assert current-session state rejects it deterministically
