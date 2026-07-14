# Q2914: add_trade_record allows stale offer intent to settle against fresh state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_trade_record` and control previously valid offer blobs replayed after wallet state changed so that `TradeStore.add_trade_record` in `chia/wallet/trading/trade_store.py` executes a path where reuse stale offer payloads in `add_trade_record` after the referenced wallet state moved on, violating the invariant that an old offer payload must not settle once the underlying spendable state has materially changed and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/trading/trade_store.py:164 `TradeStore.add_trade_record`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_trade_record`
- Attacker controls: previously valid offer blobs replayed after wallet state changed
- Exploit idea: reuse stale offer payloads in `add_trade_record` after the referenced wallet state moved on
- Invariant to test: an old offer payload must not settle once the underlying spendable state has materially changed
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay a formerly valid offer through `chia/wallet/trading/trade_store.py:add_trade_record` after wallet state changes and assert settlement is rejected
