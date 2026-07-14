# Q3872: add_spend applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_spend` and control batched spends, multi-coin updates, and partial-failure ordering so that `WalletSingletonStore.add_spend` in `chia/wallet/wallet_singleton_store.py` executes a path where make `add_spend` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_singleton_store.py:84 `WalletSingletonStore.add_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_spend`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `add_spend` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/wallet_singleton_store.py:add_spend` and assert no partial failure rewrites unrelated valid spend outcomes
