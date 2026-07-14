# Q1984: request_mempool_transactions applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach P2P message handler `request_mempool_transactions` and control batched spends, multi-coin updates, and partial-failure ordering so that `CrawlerAPI.request_mempool_transactions` in `chia/seeder/crawler_api.py` executes a path where make `request_mempool_transactions` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/seeder/crawler_api.py:104 `CrawlerAPI.request_mempool_transactions`
- Entrypoint: P2P message handler `request_mempool_transactions`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `request_mempool_transactions` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/seeder/crawler_api.py:request_mempool_transactions` and assert no partial failure rewrites unrelated valid spend outcomes
