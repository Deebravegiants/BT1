# Q2519: generate_unsigned_spendbundle accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_unsigned_spendbundle` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `NFTWallet.generate_unsigned_spendbundle` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `generate_unsigned_spendbundle` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:623 `NFTWallet.generate_unsigned_spendbundle`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_unsigned_spendbundle`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `generate_unsigned_spendbundle` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/wallet/nft_wallet/nft_wallet.py:generate_unsigned_spendbundle` and assert owner state stays canonical
