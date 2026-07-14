# Q1811: generate_launcher_spend applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach pool wallet or singleton spend flow reaching `generate_launcher_spend` and control batched spends, multi-coin updates, and partial-failure ordering so that `PoolWallet.generate_launcher_spend` in `chia/pools/pool_wallet.py` executes a path where make `generate_launcher_spend` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/pools/pool_wallet.py:545 `PoolWallet.generate_launcher_spend`
- Entrypoint: pool wallet or singleton spend flow reaching `generate_launcher_spend`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `generate_launcher_spend` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/pools/pool_wallet.py:generate_launcher_spend` and assert no partial failure rewrites unrelated valid spend outcomes
