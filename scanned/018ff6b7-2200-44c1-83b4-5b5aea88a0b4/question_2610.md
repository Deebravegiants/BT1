# Q2610: leave_pool mutates NFT ownership with inconsistent singleton state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `leave_pool` and control singleton lineage, DID bindings, and transfer or bulk-operation parameters so that `PlotNFT2Wallet.leave_pool` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `leave_pool` mutate NFT ownership or singleton state even though lineage and current-owner context disagree, violating the invariant that NFT singleton lineage, DID binding, and owner state must move together or not at all and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:280 `PlotNFT2Wallet.leave_pool`
- Entrypoint: wallet RPC or wallet sync flow reaching `leave_pool`
- Attacker controls: singleton lineage, DID bindings, and transfer or bulk-operation parameters
- Exploit idea: make `leave_pool` mutate NFT ownership or singleton state even though lineage and current-owner context disagree
- Invariant to test: NFT singleton lineage, DID binding, and owner state must move together or not at all
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: simulate stale NFT singleton lineage into `chia/wallet/plotnft_wallet/plotnft_wallet.py:leave_pool` and assert ownership or DID changes never commit
