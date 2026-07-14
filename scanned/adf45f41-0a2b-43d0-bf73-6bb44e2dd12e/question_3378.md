# Q3378: delete_nft_by_nft_id accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `delete_nft_by_nft_id` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `WalletNftStore.delete_nft_by_nft_id` in `chia/wallet/wallet_nft_store.py` executes a path where make `delete_nft_by_nft_id` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_nft_store.py:76 `WalletNftStore.delete_nft_by_nft_id`
- Entrypoint: wallet RPC or wallet sync flow reaching `delete_nft_by_nft_id`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `delete_nft_by_nft_id` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/wallet/wallet_nft_store.py:delete_nft_by_nft_id` and assert owner state stays canonical
