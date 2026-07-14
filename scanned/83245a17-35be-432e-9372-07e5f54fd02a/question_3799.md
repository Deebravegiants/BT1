# Q3799: check_offer_validity aliases offered and requested assets after parsing

## Question
Can an unprivileged attacker reach RPC route `check_offer_validity` and control offer bytes, puzzle drivers, asset ids, and settlement ordering so that `WalletRpcApi.check_offer_validity` in `chia/wallet/wallet_rpc_api.py` executes a path where make `check_offer_validity` parse or summarize one economic intent while the settlement path executes another, violating the invariant that offer intent, summary, and settlement must describe the same asset movements and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:2189 `WalletRpcApi.check_offer_validity`
- Entrypoint: RPC route `check_offer_validity`
- Attacker controls: offer bytes, puzzle drivers, asset ids, and settlement ordering
- Exploit idea: make `check_offer_validity` parse or summarize one economic intent while the settlement path executes another
- Invariant to test: offer intent, summary, and settlement must describe the same asset movements
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: round-trip crafted offer payloads through `chia/wallet/wallet_rpc_api.py:check_offer_validity` and compare parsed summaries against actual settlement side effects
