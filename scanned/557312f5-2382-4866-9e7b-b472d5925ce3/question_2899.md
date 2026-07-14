# Q2899: check_offer_validity allows stale offer intent to settle against fresh state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `check_offer_validity` and control previously valid offer blobs replayed after wallet state changed so that `TradeManager.check_offer_validity` in `chia/wallet/trade_manager.py` executes a path where reuse stale offer payloads in `check_offer_validity` after the referenced wallet state moved on, violating the invariant that an old offer payload must not settle once the underlying spendable state has materially changed and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/trade_manager.py:670 `TradeManager.check_offer_validity`
- Entrypoint: wallet RPC or wallet sync flow reaching `check_offer_validity`
- Attacker controls: previously valid offer blobs replayed after wallet state changed
- Exploit idea: reuse stale offer payloads in `check_offer_validity` after the referenced wallet state moved on
- Invariant to test: an old offer payload must not settle once the underlying spendable state has materially changed
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: replay a formerly valid offer through `chia/wallet/trade_manager.py:check_offer_validity` after wallet state changes and assert settlement is rejected
