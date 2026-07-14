# Q1694: claim_pool_rewards attributes reward-producing farming state to the wrong context

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `claim_pool_rewards` and control proof, challenge, and payout-linked farming state that should map to one reward context so that `PlotNFT.claim_pool_rewards` in `chia/pools/plotnft_drivers.py` executes a path where make `claim_pool_rewards` attribute reward-producing farming state to the wrong proof or payout context, violating the invariant that reward-producing proof state must remain bound to the correct harvester, farmer, and payout context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/pools/plotnft_drivers.py:589 `PlotNFT.claim_pool_rewards`
- Entrypoint: pool wallet or singleton spend flow reaching `claim_pool_rewards`
- Attacker controls: proof, challenge, and payout-linked farming state that should map to one reward context
- Exploit idea: make `claim_pool_rewards` attribute reward-producing farming state to the wrong proof or payout context
- Invariant to test: reward-producing proof state must remain bound to the correct harvester, farmer, and payout context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: swap proof-to-payout context around `chia/pools/plotnft_drivers.py:claim_pool_rewards` and assert rewards cannot be attributed across sessions or peers
