# Q793: add_transaction_semaphore applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `add_transaction_semaphore` and control batched spends, multi-coin updates, and partial-failure ordering so that `FullNode.add_transaction_semaphore` in `chia/full_node/full_node.py` executes a path where make `add_transaction_semaphore` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/full_node.py:459 `FullNode.add_transaction_semaphore`
- Entrypoint: full node mempool, sync, or peer flow reaching `add_transaction_semaphore`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `add_transaction_semaphore` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/full_node/full_node.py:add_transaction_semaphore` and assert no partial failure rewrites unrelated valid spend outcomes
