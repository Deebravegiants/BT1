# Q1692: claim_pool_rewards trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `claim_pool_rewards` and control signage-point, partial-proof, or solver-response contents and timing so that `PlotNFT.claim_pool_rewards` in `chia/pools/plotnft_drivers.py` executes a path where make `claim_pool_rewards` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/pools/plotnft_drivers.py:589 `PlotNFT.claim_pool_rewards`
- Entrypoint: pool wallet or singleton spend flow reaching `claim_pool_rewards`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `claim_pool_rewards` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/pools/plotnft_drivers.py:claim_pool_rewards` and assert current-session state rejects it deterministically
