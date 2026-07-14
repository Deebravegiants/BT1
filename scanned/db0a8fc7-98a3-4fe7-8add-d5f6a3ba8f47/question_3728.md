# Q3728: send_transaction applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach RPC route `send_transaction` and control batched spends, multi-coin updates, and partial-failure ordering so that `WalletRpcApi.send_transaction` in `chia/wallet/wallet_rpc_api.py` executes a path where make `send_transaction` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:1527 `WalletRpcApi.send_transaction`
- Entrypoint: RPC route `send_transaction`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `send_transaction` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/wallet_rpc_api.py:send_transaction` and assert no partial failure rewrites unrelated valid spend outcomes
