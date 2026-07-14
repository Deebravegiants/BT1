# Q1696: join_pool mutates NFT ownership with inconsistent singleton state

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `join_pool` and control singleton lineage, DID bindings, and transfer or bulk-operation parameters so that `PlotNFT.join_pool` in `chia/pools/plotnft_drivers.py` executes a path where make `join_pool` mutate NFT ownership or singleton state even though lineage and current-owner context disagree, violating the invariant that NFT singleton lineage, DID binding, and owner state must move together or not at all and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/pools/plotnft_drivers.py:643 `PlotNFT.join_pool`
- Entrypoint: pool wallet or singleton spend flow reaching `join_pool`
- Attacker controls: singleton lineage, DID bindings, and transfer or bulk-operation parameters
- Exploit idea: make `join_pool` mutate NFT ownership or singleton state even though lineage and current-owner context disagree
- Invariant to test: NFT singleton lineage, DID binding, and owner state must move together or not at all
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: simulate stale NFT singleton lineage into `chia/pools/plotnft_drivers.py:join_pool` and assert ownership or DID changes never commit
