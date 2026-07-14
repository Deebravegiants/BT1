# Q2526: make_nft1_offer mutates NFT ownership with inconsistent singleton state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `make_nft1_offer` and control singleton lineage, DID bindings, and transfer or bulk-operation parameters so that `NFTWallet.make_nft1_offer` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `make_nft1_offer` mutate NFT ownership or singleton state even though lineage and current-owner context disagree, violating the invariant that NFT singleton lineage, DID binding, and owner state must move together or not at all and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:726 `NFTWallet.make_nft1_offer`
- Entrypoint: wallet RPC or wallet sync flow reaching `make_nft1_offer`
- Attacker controls: singleton lineage, DID bindings, and transfer or bulk-operation parameters
- Exploit idea: make `make_nft1_offer` mutate NFT ownership or singleton state even though lineage and current-owner context disagree
- Invariant to test: NFT singleton lineage, DID binding, and owner state must move together or not at all
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: simulate stale NFT singleton lineage into `chia/wallet/nft_wallet/nft_wallet.py:make_nft1_offer` and assert ownership or DID changes never commit
