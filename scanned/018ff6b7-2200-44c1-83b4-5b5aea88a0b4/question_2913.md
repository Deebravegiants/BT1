# Q2913: add_trade_record settles an offer with mismatched lineage or ownership state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_trade_record` and control offer payloads that reference stale ownership, lineage, or settlement context so that `TradeStore.add_trade_record` in `chia/wallet/trading/trade_store.py` executes a path where push `add_trade_record` to settle an offer against stale lineage, ownership, or reservation state, violating the invariant that offer settlement must use current ownership and lineage, not stale or cross-offer state and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/trading/trade_store.py:164 `TradeStore.add_trade_record`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_trade_record`
- Attacker controls: offer payloads that reference stale ownership, lineage, or settlement context
- Exploit idea: push `add_trade_record` to settle an offer against stale lineage, ownership, or reservation state
- Invariant to test: offer settlement must use current ownership and lineage, not stale or cross-offer state
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: settle an offer against stale lineage in a local integration test and assert `chia/wallet/trading/trade_store.py:add_trade_record` rejects it before state mutation
