# Q2898: check_offer_validity settles an offer with mismatched lineage or ownership state

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `check_offer_validity` and control offer payloads that reference stale ownership, lineage, or settlement context so that `TradeManager.check_offer_validity` in `chia/wallet/trade_manager.py` executes a path where push `check_offer_validity` to settle an offer against stale lineage, ownership, or reservation state, violating the invariant that offer settlement must use current ownership and lineage, not stale or cross-offer state and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/trade_manager.py:670 `TradeManager.check_offer_validity`
- Entrypoint: wallet RPC or wallet sync flow reaching `check_offer_validity`
- Attacker controls: offer payloads that reference stale ownership, lineage, or settlement context
- Exploit idea: push `check_offer_validity` to settle an offer against stale lineage, ownership, or reservation state
- Invariant to test: offer settlement must use current ownership and lineage, not stale or cross-offer state
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: settle an offer against stale lineage in a local integration test and assert `chia/wallet/trade_manager.py:check_offer_validity` rejects it before state mutation
