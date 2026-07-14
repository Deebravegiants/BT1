# Q2858: select_coins desynchronizes coin accounting from spend execution

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `select_coins` and control bundle contents that make additions, removals, and fee accounting disagree so that `RemoteWallet.select_coins` in `chia/wallet/remote_wallet/remote_wallet.py` executes a path where make `select_coins` commit balance or ownership effects that no longer match the executed spend conditions, violating the invariant that coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/remote_wallet/remote_wallet.py:142 `RemoteWallet.select_coins`
- Entrypoint: wallet RPC or wallet sync flow reaching `select_coins`
- Attacker controls: bundle contents that make additions, removals, and fee accounting disagree
- Exploit idea: make `select_coins` commit balance or ownership effects that no longer match the executed spend conditions
- Invariant to test: coin additions, removals, fees, and ownership effects must match the executed CLVM spend semantics exactly
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: instrument `chia/wallet/remote_wallet/remote_wallet.py:select_coins` and assert additions, removals, and fee totals exactly match CLVM execution results for crafted bundles
