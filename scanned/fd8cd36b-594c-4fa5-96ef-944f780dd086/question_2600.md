# Q2600: claim_rewards lets plot sync state suppress honest farming actions

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `claim_rewards` and control plot-sync deltas, stale plot lists, and peer identity reuse so that `PlotNFT2Wallet.claim_rewards` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `claim_rewards` suppress or misapply honest plot state using attacker-driven sync deltas, violating the invariant that plot sync state must not suppress honest plots or stall valid farming actions for long periods and leading to Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:137 `PlotNFT2Wallet.claim_rewards`
- Entrypoint: wallet RPC or wallet sync flow reaching `claim_rewards`
- Attacker controls: plot-sync deltas, stale plot lists, and peer identity reuse
- Exploit idea: make `claim_rewards` suppress or misapply honest plot state using attacker-driven sync deltas
- Invariant to test: plot sync state must not suppress honest plots or stall valid farming actions for long periods
- Expected Immunefi impact: Permanent or long-lived inability for honest nodes, wallets, farmers, harvesters, or timelords to process valid blocks, spend bundles, sync updates, pool actions, or Data Layer updates under normal network assumptions
- Fast validation: reorder plot-sync deltas into `chia/wallet/plotnft_wallet/plotnft_wallet.py:claim_rewards` and assert honest plots remain visible and actionable
