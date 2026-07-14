# Q3400: update_pending_transaction accepts NFT metadata or DID updates without preserving ownership invariants

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `update_pending_transaction` and control metadata uri sets, DID changes, status flips, and transfer sequencing so that `WalletNftStore.update_pending_transaction` in `chia/wallet/wallet_nft_store.py` executes a path where make `update_pending_transaction` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant, violating the invariant that NFT metadata and DID updates must preserve canonical ownership and singleton continuity and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_nft_store.py:104 `WalletNftStore.update_pending_transaction`
- Entrypoint: wallet RPC or wallet sync flow reaching `update_pending_transaction`
- Attacker controls: metadata uri sets, DID changes, status flips, and transfer sequencing
- Exploit idea: make `update_pending_transaction` preserve attacker-controlled metadata or DID changes while breaking the NFT's ownership invariant
- Invariant to test: NFT metadata and DID updates must preserve canonical ownership and singleton continuity
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz metadata and DID update sequencing through `chia/wallet/wallet_nft_store.py:update_pending_transaction` and assert owner state stays canonical
