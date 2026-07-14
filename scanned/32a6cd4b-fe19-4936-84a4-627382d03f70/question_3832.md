# Q3832: get_coin_records applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach RPC route `get_coin_records` and control batched spends, multi-coin updates, and partial-failure ordering so that `WalletRpcApi.get_coin_records` in `chia/wallet/wallet_rpc_api.py` executes a path where make `get_coin_records` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:3043 `WalletRpcApi.get_coin_records`
- Entrypoint: RPC route `get_coin_records`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `get_coin_records` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/wallet_rpc_api.py:get_coin_records` and assert no partial failure rewrites unrelated valid spend outcomes
