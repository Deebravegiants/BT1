# Q918: new_transaction applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach P2P message handler `new_transaction` and control batched spends, multi-coin updates, and partial-failure ordering so that `FullNodeAPI.new_transaction` in `chia/full_node/full_node_api.py` executes a path where make `new_transaction` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/full_node_api.py:223 `FullNodeAPI.new_transaction`
- Entrypoint: P2P message handler `new_transaction`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `new_transaction` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/full_node/full_node_api.py:new_transaction` and assert no partial failure rewrites unrelated valid spend outcomes
