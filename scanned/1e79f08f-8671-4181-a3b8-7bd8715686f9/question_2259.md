# Q2259: create_new_did_wallet_from_coin_spend applies attacker-controlled batch semantics inconsistently

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_did_wallet_from_coin_spend` and control batched spends, multi-coin updates, and partial-failure ordering so that `DIDWallet.create_new_did_wallet_from_coin_spend` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `create_new_did_wallet_from_coin_spend` apply a partially failing batch as if its individual spends still shared one security outcome, violating the invariant that batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:177 `DIDWallet.create_new_did_wallet_from_coin_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_did_wallet_from_coin_spend`
- Attacker controls: batched spends, multi-coin updates, and partial-failure ordering
- Exploit idea: make `create_new_did_wallet_from_coin_spend` apply a partially failing batch as if its individual spends still shared one security outcome
- Invariant to test: batch semantics must not let one attacker-chosen partial failure rewrite the security outcome of unrelated valid spends
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: inject a mixed-success batch into `chia/wallet/did_wallet/did_wallet.py:create_new_did_wallet_from_coin_spend` and assert no partial failure rewrites unrelated valid spend outcomes
