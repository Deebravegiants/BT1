# Q3081: coin_added mixes CAT accounting with XCH or offer settlement state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `coin_added` and control CAT-to-XCH settlement inputs, multi-asset specs, and spend ordering so that `CRCATWallet.coin_added` in `chia/wallet/vc_wallet/cr_cat_wallet.py` executes a path where make `coin_added` settle CAT and XCH legs under mismatched accounting assumptions, violating the invariant that CAT settlement must not create or destroy value when crossing XCH, CAT, and offer bookkeeping and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_wallet.py:208 `CRCATWallet.coin_added`
- Entrypoint: wallet RPC or wallet sync flow reaching `coin_added`
- Attacker controls: CAT-to-XCH settlement inputs, multi-asset specs, and spend ordering
- Exploit idea: make `coin_added` settle CAT and XCH legs under mismatched accounting assumptions
- Invariant to test: CAT settlement must not create or destroy value when crossing XCH, CAT, and offer bookkeeping
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: settle CAT/XCH offers with crafted discrepancy inputs and assert `chia/wallet/vc_wallet/cr_cat_wallet.py:coin_added` preserves total value and asset identity
