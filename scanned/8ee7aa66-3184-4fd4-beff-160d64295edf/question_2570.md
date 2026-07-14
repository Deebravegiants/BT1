# Q2570: add_pool_reward mutates NFT ownership with inconsistent singleton state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_pool_reward` and control singleton lineage, DID bindings, and transfer or bulk-operation parameters so that `PlotNFTStore.add_pool_reward` in `chia/wallet/plotnft_wallet/plotnft_store.py` executes a path where make `add_pool_reward` mutate NFT ownership or singleton state even though lineage and current-owner context disagree, violating the invariant that NFT singleton lineage, DID binding, and owner state must move together or not at all and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_store.py:113 `PlotNFTStore.add_pool_reward`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_pool_reward`
- Attacker controls: singleton lineage, DID bindings, and transfer or bulk-operation parameters
- Exploit idea: make `add_pool_reward` mutate NFT ownership or singleton state even though lineage and current-owner context disagree
- Invariant to test: NFT singleton lineage, DID binding, and owner state must move together or not at all
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: simulate stale NFT singleton lineage into `chia/wallet/plotnft_wallet/plotnft_store.py:add_pool_reward` and assert ownership or DID changes never commit
