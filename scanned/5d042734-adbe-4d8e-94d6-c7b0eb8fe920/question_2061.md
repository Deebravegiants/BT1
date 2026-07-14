# Q2061: check_orphaned_unfinished_block trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach P2P message handler `check_orphaned_unfinished_block` and control signage-point, partial-proof, or solver-response contents and timing so that `TimelordAPI.check_orphaned_unfinished_block` in `chia/timelord/timelord_api.py` executes a path where make `check_orphaned_unfinished_block` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/timelord/timelord_api.py:122 `TimelordAPI.check_orphaned_unfinished_block`
- Entrypoint: P2P message handler `check_orphaned_unfinished_block`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `check_orphaned_unfinished_block` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/timelord/timelord_api.py:check_orphaned_unfinished_block` and assert current-session state rejects it deterministically
