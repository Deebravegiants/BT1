# Q2461: remove_coin accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_coin` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `NFTWallet.remove_coin` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `remove_coin` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:281 `NFTWallet.remove_coin`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_coin`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `remove_coin` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/wallet/nft_wallet/nft_wallet.py:remove_coin` and assert owner state stays canonical
