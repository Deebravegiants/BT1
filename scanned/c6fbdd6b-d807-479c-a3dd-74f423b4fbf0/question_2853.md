# Q2853: coin_added applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `coin_added` and control batched spends, multi-coin updates, and partial-failure ordering so that `RemoteWallet.coin_added` in `chia/wallet/remote_wallet/remote_wallet.py` executes a path where make `coin_added` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/remote_wallet/remote_wallet.py:137 `RemoteWallet.coin_added`
- Entrypoint: wallet RPC or wallet sync flow reaching `coin_added`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `coin_added` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/remote_wallet/remote_wallet.py:coin_added` and assert no partial failure rewrites unrelated valid spend outcomes
