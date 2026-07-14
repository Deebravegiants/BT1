# Q2098: create_from_puzzle_info applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_from_puzzle_info` and control batched spends, multi-coin updates, and partial-failure ordering so that `CATWallet.create_from_puzzle_info` in `chia/wallet/cat_wallet/cat_wallet.py` executes a path where make `create_from_puzzle_info` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/cat_wallet/cat_wallet.py:249 `CATWallet.create_from_puzzle_info`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_from_puzzle_info`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `create_from_puzzle_info` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/cat_wallet/cat_wallet.py:create_from_puzzle_info` and assert no partial failure rewrites unrelated valid spend outcomes
