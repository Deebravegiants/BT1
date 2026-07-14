# Q2071: new_unfinished_block_timelord trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach P2P message handler `new_unfinished_block_timelord` and control signage-point, partial-proof, or solver-response contents and timing so that `TimelordAPI.new_unfinished_block_timelord` in `chia/timelord/timelord_api.py` executes a path where make `new_unfinished_block_timelord` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/timelord/timelord_api.py:143 `TimelordAPI.new_unfinished_block_timelord`
- Entrypoint: P2P message handler `new_unfinished_block_timelord`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `new_unfinished_block_timelord` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/timelord/timelord_api.py:new_unfinished_block_timelord` and assert current-session state rejects it deterministically
