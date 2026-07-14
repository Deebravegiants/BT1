# Q1353: new_signage_point trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_signage_point` and control signage-point, partial-proof, or solver-response contents and timing so that `FullNodeStore.new_signage_point` in `chia/full_node/full_node_store.py` executes a path where make `new_signage_point` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/full_node/full_node_store.py:709 `FullNodeStore.new_signage_point`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_signage_point`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `new_signage_point` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/full_node/full_node_store.py:new_signage_point` and assert current-session state rejects it deterministically
