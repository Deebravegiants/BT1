# Q3340: remove_interested_coin_id applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_interested_coin_id` and control batched spends, multi-coin updates, and partial-failure ordering so that `WalletInterestedStore.remove_interested_coin_id` in `chia/wallet/wallet_interested_store.py` executes a path where make `remove_interested_coin_id` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_interested_store.py:51 `WalletInterestedStore.remove_interested_coin_id`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_interested_coin_id`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `remove_interested_coin_id` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/wallet_interested_store.py:remove_interested_coin_id` and assert no partial failure rewrites unrelated valid spend outcomes
