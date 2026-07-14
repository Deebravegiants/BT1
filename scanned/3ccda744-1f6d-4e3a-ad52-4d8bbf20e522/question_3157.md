# Q3157: create_new_vc_wallet reuses stale VC state across proof or spend flows

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_vc_wallet` and control stale VC records or proof context replayed after state transitions so that `VCWallet.create_new_vc_wallet` in `chia/wallet/vc_wallet/vc_wallet.py` executes a path where make `create_new_vc_wallet` accept stale VC proof or record state after the credential moved on, violating the invariant that old VC proof or record state must not remain authorizing after a later state transition and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/vc_wallet.py:58 `VCWallet.create_new_vc_wallet`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_vc_wallet`
- Attacker controls: stale VC records or proof context replayed after state transitions
- Exploit idea: make `create_new_vc_wallet` accept stale VC proof or record state after the credential moved on
- Invariant to test: old VC proof or record state must not remain authorizing after a later state transition
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale VC state into `chia/wallet/vc_wallet/vc_wallet.py:create_new_vc_wallet` after a later transition and assert no proof or spend path still accepts it
