# Q3399: update_pending_transaction mutates NFT ownership with inconsistent singleton state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `update_pending_transaction` and control singleton lineage, DID bindings, and transfer or bulk-operation parameters so that `WalletNftStore.update_pending_transaction` in `chia/wallet/wallet_nft_store.py` executes a path where make `update_pending_transaction` mutate NFT ownership or singleton state even though lineage and current-owner context disagree, violating the invariant that NFT singleton lineage, DID binding, and owner state must move together or not at all and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_nft_store.py:104 `WalletNftStore.update_pending_transaction`
- Entrypoint: wallet RPC or wallet sync flow reaching `update_pending_transaction`
- Attacker controls: singleton lineage, DID bindings, and transfer or bulk-operation parameters
- Exploit idea: make `update_pending_transaction` mutate NFT ownership or singleton state even though lineage and current-owner context disagree
- Invariant to test: NFT singleton lineage, DID binding, and owner state must move together or not at all
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: simulate stale NFT singleton lineage into `chia/wallet/wallet_nft_store.py:update_pending_transaction` and assert ownership or DID changes never commit
