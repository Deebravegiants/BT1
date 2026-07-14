# Q2638: new_peak accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `new_peak` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `PlotNFT2Wallet.new_peak` in `chia/wallet/plotnft_wallet/plotnft_wallet.py` executes a path where make `new_peak` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/plotnft_wallet/plotnft_wallet.py:472 `PlotNFT2Wallet.new_peak`
- Entrypoint: wallet RPC or wallet sync flow reaching `new_peak`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `new_peak` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/wallet/plotnft_wallet/plotnft_wallet.py:new_peak` and assert owner state stays canonical
