# Q3044: spend_many reuses stale VC state across proof or spend flows

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `spend_many` and control stale VC records or proof context replayed after state transitions so that `CRCAT.spend_many` in `chia/wallet/vc_wallet/cr_cat_drivers.py` executes a path where make `spend_many` accept stale VC proof or record state after the credential moved on, violating the invariant that old VC proof or record state must not remain authorizing after a later state transition and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_drivers.py:515 `CRCAT.spend_many`
- Entrypoint: wallet RPC or wallet sync flow reaching `spend_many`
- Attacker controls: stale VC records or proof context replayed after state transitions
- Exploit idea: make `spend_many` accept stale VC proof or record state after the credential moved on
- Invariant to test: old VC proof or record state must not remain authorizing after a later state transition
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale VC state into `chia/wallet/vc_wallet/cr_cat_drivers.py:spend_many` after a later transition and assert no proof or spend path still accepts it
