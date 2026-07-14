# Q2428: create_new_nft_wallet accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_nft_wallet` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `NFTWallet.create_new_nft_wallet` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `create_new_nft_wallet` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:88 `NFTWallet.create_new_nft_wallet`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_nft_wallet`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `create_new_nft_wallet` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/wallet/nft_wallet/nft_wallet.py:create_new_nft_wallet` and assert owner state stays canonical
