# Q3364: add_unacknowledged_coin_state applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_unacknowledged_coin_state` and control batched spends, multi-coin updates, and partial-failure ordering so that `WalletInterestedStore.add_unacknowledged_coin_state` in `chia/wallet/wallet_interested_store.py` executes a path where make `add_unacknowledged_coin_state` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_interested_store.py:128 `WalletInterestedStore.add_unacknowledged_coin_state`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_unacknowledged_coin_state`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `add_unacknowledged_coin_state` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/wallet_interested_store.py:add_unacknowledged_coin_state` and assert no partial failure rewrites unrelated valid spend outcomes
