# Q2527: make_nft1_offer accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `make_nft1_offer` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `NFTWallet.make_nft1_offer` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `make_nft1_offer` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:726 `NFTWallet.make_nft1_offer`
- Entrypoint: wallet RPC or wallet sync flow reaching `make_nft1_offer`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `make_nft1_offer` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/wallet/nft_wallet/nft_wallet.py:make_nft1_offer` and assert owner state stays canonical
