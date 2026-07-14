# Q2900: check_offer_validity trusts attacker-shaped state across an internal boundary

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `check_offer_validity` and control security-critical fields that cross from one production layer to another without changing the external attacker model so that `TradeManager.check_offer_validity` in `chia/wallet/trade_manager.py` executes a path where make `check_offer_validity` trust attacker-shaped state that another nearby layer should have revalidated before use, violating the invariant that every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/trade_manager.py:670 `TradeManager.check_offer_validity`
- Entrypoint: wallet RPC or wallet sync flow reaching `check_offer_validity`
- Attacker controls: security-critical fields that cross from one production layer to another without changing the external attacker model
- Exploit idea: make `check_offer_validity` trust attacker-shaped state that another nearby layer should have revalidated before use
- Invariant to test: every boundary between parsing, validation, storage, and execution must revalidate security-critical attacker-controlled fields before trusting them
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: drive one attacker-controlled object across adjacent layers into `chia/wallet/trade_manager.py:check_offer_validity` and assert the receiving layer revalidates every security-critical field before trusting it
