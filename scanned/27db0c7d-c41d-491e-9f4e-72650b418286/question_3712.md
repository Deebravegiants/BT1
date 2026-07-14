# Q3712: split_coins applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach RPC route `split_coins` and control batched spends, multi-coin updates, and partial-failure ordering so that `WalletRpcApi.split_coins` in `chia/wallet/wallet_rpc_api.py` executes a path where make `split_coins` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1415 `WalletRpcApi.split_coins`
- Entrypoint: RPC route `split_coins`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `split_coins` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/wallet_rpc_api.py:split_coins` and assert no partial failure rewrites unrelated valid spend outcomes
