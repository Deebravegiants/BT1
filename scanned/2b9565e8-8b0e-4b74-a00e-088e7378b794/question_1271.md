# Q1271: get_coin_records_by_names applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach RPC route `get_coin_records_by_names` and control batched spends, multi-coin updates, and partial-failure ordering so that `FullNodeRpcApi.get_coin_records_by_names` in `chia/full_node/full_node_rpc_api.py` executes a path where make `get_coin_records_by_names` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/full_node/full_node_rpc_api.py:753 `FullNodeRpcApi.get_coin_records_by_names`
- Entrypoint: RPC route `get_coin_records_by_names`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `get_coin_records_by_names` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/full_node/full_node_rpc_api.py:get_coin_records_by_names` and assert no partial failure rewrites unrelated valid spend outcomes
