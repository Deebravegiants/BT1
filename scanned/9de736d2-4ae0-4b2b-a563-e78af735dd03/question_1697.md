# Q1697: join_pool accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `join_pool` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `PlotNFT.join_pool` in `chia/pools/plotnft_drivers.py` executes a path where make `join_pool` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/pools/plotnft_drivers.py:643 `PlotNFT.join_pool`
- Entrypoint: pool wallet or singleton spend flow reaching `join_pool`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `join_pool` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/pools/plotnft_drivers.py:join_pool` and assert owner state stays canonical
