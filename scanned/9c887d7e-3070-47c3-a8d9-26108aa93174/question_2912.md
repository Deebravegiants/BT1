# Q2912: add_trade_record races offer cancellation against settlement

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_trade_record` and control offer creation, take, and cancel timing under the same visible offer state so that `TradeStore.add_trade_record` in `chia/wallet/trading/trade_store.py` executes a path where race `add_trade_record` between cancellation and acceptance so the same offer state authorizes two incompatible outcomes, violating the invariant that an offer must not be simultaneously cancellable and settleable against the same state and leading to Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins?

## Target
- File/function: chia/wallet/trading/trade_store.py:164 `TradeStore.add_trade_record`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_trade_record`
- Attacker controls: offer creation, take, and cancel timing under the same visible offer state
- Exploit idea: race `add_trade_record` between cancellation and acceptance so the same offer state authorizes two incompatible outcomes
- Invariant to test: an offer must not be simultaneously cancellable and settleable against the same state
- Expected Immunefi impact: Unauthorized creation, spend, clawback bypass, reward diversion, offer settlement, or accounting change affecting XCH, CATs, NFTs, DIDs, VCs, pool wallets, singleton-controlled assets, or Data Layer-linked coins
- Fast validation: race take/cancel flows into `chia/wallet/trading/trade_store.py:add_trade_record` and assert only one terminal state is reachable for the same offer
