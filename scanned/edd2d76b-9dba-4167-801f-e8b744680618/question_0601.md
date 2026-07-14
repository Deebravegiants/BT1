# Q601: respond_signatures trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach P2P message handler `respond_signatures` and control signage-point, partial-proof, or solver-response contents and timing so that `FarmerAPI.respond_signatures` in `chia/farmer/farmer_api.py` executes a path where make `respond_signatures` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/farmer/farmer_api.py:603 `FarmerAPI.respond_signatures`
- Entrypoint: P2P message handler `respond_signatures`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `respond_signatures` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/farmer/farmer_api.py:respond_signatures` and assert current-session state rejects it deterministically
