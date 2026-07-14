# Q2256: create_new_did_wallet_from_coin_spend desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_did_wallet_from_coin_spend` and control bundle contents that make additions, removals, and fee accounting disagree so that `DIDWallet.create_new_did_wallet_from_coin_spend` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `create_new_did_wallet_from_coin_spend` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:177 `DIDWallet.create_new_did_wallet_from_coin_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_did_wallet_from_coin_spend`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `create_new_did_wallet_from_coin_spend` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/wallet/did_wallet/did_wallet.py:create_new_did_wallet_from_coin_spend` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
