# Q831: signage_point_post_processing trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `signage_point_post_processing` and control signage-point, partial-proof, or solver-response contents and timing so that `FullNode.signage_point_post_processing` in `chia/full_node/full_node.py` executes a path where make `signage_point_post_processing` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/full_node/full_node.py:1847 `FullNode.signage_point_post_processing`
- Entrypoint: full node mempool, sync, or peer flow reaching `signage_point_post_processing`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `signage_point_post_processing` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/full_node/full_node.py:signage_point_post_processing` and assert current-session state rejects it deterministically
