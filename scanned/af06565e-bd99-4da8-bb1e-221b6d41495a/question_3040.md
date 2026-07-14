# Q3040: spend_many applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `spend_many` and control batched spends, multi-coin updates, and partial-failure ordering so that `CRCAT.spend_many` in `chia/wallet/vc_wallet/cr_cat_drivers.py` executes a path where make `spend_many` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_drivers.py:515 `CRCAT.spend_many`
- Entrypoint: wallet RPC or wallet sync flow reaching `spend_many`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `spend_many` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/vc_wallet/cr_cat_drivers.py:spend_many` and assert no partial failure rewrites unrelated valid spend outcomes
