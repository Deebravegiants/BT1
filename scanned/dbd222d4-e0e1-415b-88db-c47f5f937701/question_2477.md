# Q2477: update_coin_status applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `update_coin_status` and control batched spends, multi-coin updates, and partial-failure ordering so that `NFTWallet.update_coin_status` in `chia/wallet/nft_wallet/nft_wallet.py` executes a path where make `update_coin_status` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/nft_wallet/nft_wallet.py:482 `NFTWallet.update_coin_status`
- Entrypoint: wallet RPC or wallet sync flow reaching `update_coin_status`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `update_coin_status` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/nft_wallet/nft_wallet.py:update_coin_status` and assert no partial failure rewrites unrelated valid spend outcomes
