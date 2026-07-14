# Q1638: request_plots trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach P2P message handler `request_plots` and control signage-point, partial-proof, or solver-response contents and timing so that `HarvesterAPI.request_plots` in `chia/harvester/harvester_api.py` executes a path where make `request_plots` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/harvester/harvester_api.py:529 `HarvesterAPI.request_plots`
- Entrypoint: P2P message handler `request_plots`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `request_plots` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/harvester/harvester_api.py:request_plots` and assert current-session state rejects it deterministically
