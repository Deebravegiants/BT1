# Q1025: new_signage_point_or_end_of_sub_slot trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach P2P message handler `new_signage_point_or_end_of_sub_slot` and control signage-point, partial-proof, or solver-response contents and timing so that `FullNodeAPI.new_signage_point_or_end_of_sub_slot` in `chia/full_node/full_node_api.py` executes a path where make `new_signage_point_or_end_of_sub_slot` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/full_node/full_node_api.py:651 `FullNodeAPI.new_signage_point_or_end_of_sub_slot`
- Entrypoint: P2P message handler `new_signage_point_or_end_of_sub_slot`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `new_signage_point_or_end_of_sub_slot` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/full_node/full_node_api.py:new_signage_point_or_end_of_sub_slot` and assert current-session state rejects it deterministically
