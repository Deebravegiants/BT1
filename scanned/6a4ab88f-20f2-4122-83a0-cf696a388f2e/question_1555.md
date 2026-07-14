# Q1555: remove_coin_subscriptions applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `remove_coin_subscriptions` and control batched spends, multi-coin updates, and partial-failure ordering so that `PeerSubscriptions.remove_coin_subscriptions` in `chia/full_node/subscriptions.py` executes a path where make `remove_coin_subscriptions` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/subscriptions.py:170 `PeerSubscriptions.remove_coin_subscriptions`
- Entrypoint: full node mempool, sync, or peer flow reaching `remove_coin_subscriptions`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `remove_coin_subscriptions` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/full_node/subscriptions.py:remove_coin_subscriptions` and assert no partial failure rewrites unrelated valid spend outcomes
