# Q3110: generate_signed_transaction reuses stale VC state across proof or spend flows

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_signed_transaction` and control stale VC records or proof context replayed after state transitions so that `CRCATWallet.generate_signed_transaction` in `chia/wallet/vc_wallet/cr_cat_wallet.py` executes a path where make `generate_signed_transaction` accept stale VC proof or record state after the credential moved on, violating the invariant that old VC proof or record state must not remain authorizing after a later state transition and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_wallet.py:594 `CRCATWallet.generate_signed_transaction`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_signed_transaction`
- Attacker controls: stale VC records or proof context replayed after state transitions
- Exploit idea: make `generate_signed_transaction` accept stale VC proof or record state after the credential moved on
- Invariant to test: old VC proof or record state must not remain authorizing after a later state transition
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale VC state into `chia/wallet/vc_wallet/cr_cat_wallet.py:generate_signed_transaction` after a later transition and assert no proof or spend path still accepts it
