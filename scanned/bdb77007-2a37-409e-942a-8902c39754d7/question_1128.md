# Q1128: request_puzzle_solution applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach P2P message handler `request_puzzle_solution` and control batched spends, multi-coin updates, and partial-failure ordering so that `FullNodeAPI.request_puzzle_solution` in `chia/full_node/full_node_api.py` executes a path where make `request_puzzle_solution` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/full_node_api.py:1590 `FullNodeAPI.request_puzzle_solution`
- Entrypoint: P2P message handler `request_puzzle_solution`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `request_puzzle_solution` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/full_node/full_node_api.py:request_puzzle_solution` and assert no partial failure rewrites unrelated valid spend outcomes
