# Q2599: claim_rewards trusts partial proof or signage data across stale sessions

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `claim_rewards` and control signage-point, partial-proof, or solver-response contents and timing so that `PlotNFT2Wallet.claim_rewards` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `claim_rewards` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes, violating the invariant that stale or cross-session farming proofs must never influence current valid-farming decisions and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:137 `PlotNFT2Wallet.claim_rewards`
- Entrypoint: wallet RPC or wallet sync flow reaching `claim_rewards`
- Attacker controls: signage-point, partial-proof, or solver-response contents and timing
- Exploit idea: make `claim_rewards` trust stale or cross-session partial proof state strongly enough to affect valid farming outcomes
- Invariant to test: stale or cross-session farming proofs must never influence current valid-farming decisions
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: replay stale partial-proof or signage data into `chia/wallet/plotnft_wallet/plotnft_wallet.py:claim_rewards` and assert current-session state rejects it deterministically
