# Q1688: claim_pool_rewards replays stale NFT state into a fresh ownership path

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `claim_pool_rewards` and control stale NFT singleton state replayed after ownership moved so that `PlotNFT.claim_pool_rewards` in `chia/pools/plotnft_drivers.py` executes a path where make `claim_pool_rewards` replay stale NFT singleton state into a fresh ownership transition, violating the invariant that stale NFT singleton state must not be replayable into a fresh owner-controlled path and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/pools/plotnft_drivers.py:589 `PlotNFT.claim_pool_rewards`
- Entrypoint: pool wallet or singleton spend flow reaching `claim_pool_rewards`
- Attacker controls: stale NFT singleton state replayed after ownership moved
- Exploit idea: make `claim_pool_rewards` replay stale NFT singleton state into a fresh ownership transition
- Invariant to test: stale NFT singleton state must not be replayable into a fresh owner-controlled path
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay stale NFT state after transfer into `chia/pools/plotnft_drivers.py:claim_pool_rewards` and assert the old state cannot mutate the new owner record
