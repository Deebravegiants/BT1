# Q2911: add_trade_record aliases offered and requested assets after parsing

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_trade_record` and control offer bytes, puzzle drivers, asset ids, and settlement ordering so that `TradeStore.add_trade_record` in `chia/wallet/trading/trade_store.py` executes a path where make `add_trade_record` parse or summarize one economic intent while the settlement path executes another, violating the invariant that offer intent, summary, and settlement must describe the same asset movements and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/trading/trade_store.py:164 `TradeStore.add_trade_record`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_trade_record`
- Attacker controls: offer bytes, puzzle drivers, asset ids, and settlement ordering
- Exploit idea: make `add_trade_record` parse or summarize one economic intent while the settlement path executes another
- Invariant to test: offer intent, summary, and settlement must describe the same asset movements
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: round-trip crafted offer payloads through `chia/wallet/trading/trade_store.py:add_trade_record` and compare parsed summaries against actual settlement side effects
