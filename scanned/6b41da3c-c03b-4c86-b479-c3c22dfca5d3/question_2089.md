# Q2089: create_new_cat_wallet accepts CAT lineage or asset identity that does not match the spend

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_cat_wallet` and control CAT asset ids, lineage proofs, inner puzzles, and offer/transfer parameters so that `CATWallet.create_new_cat_wallet` in `chia/wallet/cat_wallet/cat_wallet.py` executes a path where make `create_new_cat_wallet` accept CAT lineage or asset identity that does not correspond to the actual inner spend path, violating the invariant that CAT lineage, asset id, and inner puzzle identity must remain one coherent asset context and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/cat_wallet/cat_wallet.py:102 `CATWallet.create_new_cat_wallet`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_cat_wallet`
- Attacker controls: CAT asset ids, lineage proofs, inner puzzles, and offer/transfer parameters
- Exploit idea: make `create_new_cat_wallet` accept CAT lineage or asset identity that does not correspond to the actual inner spend path
- Invariant to test: CAT lineage, asset id, and inner puzzle identity must remain one coherent asset context
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: fuzz CAT lineage and asset-id mismatches into `chia/wallet/cat_wallet/cat_wallet.py:create_new_cat_wallet` and assert no spend or wallet creation path accepts them
