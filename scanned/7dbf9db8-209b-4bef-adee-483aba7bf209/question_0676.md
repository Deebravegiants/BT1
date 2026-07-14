# Q676: add_mempool_item applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_mempool_item` and control batched spends, multi-coin updates, and partial-failure ordering so that `BitcoinFeeEstimator.add_mempool_item` in `chia/full_node/bitcoin_fee_estimator.py` executes a path where make `add_mempool_item` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/bitcoin_fee_estimator.py:38 `BitcoinFeeEstimator.add_mempool_item`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_mempool_item`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `add_mempool_item` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/full_node/bitcoin_fee_estimator.py:add_mempool_item` and assert no partial failure rewrites unrelated valid spend outcomes
