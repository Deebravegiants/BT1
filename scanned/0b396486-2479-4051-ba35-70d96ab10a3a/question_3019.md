# Q3019: subscribe_to_coin_updates applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `subscribe_to_coin_updates` and control batched spends, multi-coin updates, and partial-failure ordering so that `subscribe_to_coin_updates` in `chia/wallet/util/wallet_sync_utils.py` executes a path where make `subscribe_to_coin_updates` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/util/wallet_sync_utils.py:72 `subscribe_to_coin_updates`
- Entrypoint: wallet RPC or wallet sync flow reaching `subscribe_to_coin_updates`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `subscribe_to_coin_updates` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/util/wallet_sync_utils.py:subscribe_to_coin_updates` and assert no partial failure rewrites unrelated valid spend outcomes
