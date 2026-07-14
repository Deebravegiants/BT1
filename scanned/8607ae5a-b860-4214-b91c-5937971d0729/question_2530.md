# Q2530: set_bulk_nft_did mutates NFT ownership with inconsistent singleton state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `set_bulk_nft_did` and control singleton lineage, DID bindings, and transfer or bulk-operation parameters so that `NFTWallet.set_bulk_nft_did` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `set_bulk_nft_did` mutate NFT ownership or singleton state even though lineage and current-owner context disagree, violating the invariant that NFT singleton lineage, DID binding, and owner state must move together or not at all and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:1019 `NFTWallet.set_bulk_nft_did`
- Entrypoint: wallet RPC or wallet sync flow reaching `set_bulk_nft_did`
- Attacker controls: singleton lineage, DID bindings, and transfer or bulk-operation parameters
- Exploit idea: make `set_bulk_nft_did` mutate NFT ownership or singleton state even though lineage and current-owner context disagree
- Invariant to test: NFT singleton lineage, DID binding, and owner state must move together or not at all
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: simulate stale NFT singleton lineage into `chia/wallet/nft_wallet/nft_wallet.py:set_bulk_nft_did` and assert ownership or DID changes never commit
