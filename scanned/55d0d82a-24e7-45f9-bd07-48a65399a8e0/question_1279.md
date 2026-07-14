# Q1279: push_tx applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach RPC route `push_tx` and control batched spends, multi-coin updates, and partial-failure ordering so that `FullNodeRpcApi.push_tx` in `chia/full_node/full_node_rpc_api.py` executes a path where make `push_tx` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:826 `FullNodeRpcApi.push_tx`
- Entrypoint: RPC route `push_tx`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `push_tx` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/full_node/full_node_rpc_api.py:push_tx` and assert no partial failure rewrites unrelated valid spend outcomes
