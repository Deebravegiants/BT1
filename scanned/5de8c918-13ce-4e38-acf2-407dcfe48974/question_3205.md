# Q3205: add_vc_authorization reuses stale VC state across proof or spend flows

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_vc_authorization` and control stale VC records or proof context replayed after state transitions so that `VCWallet.add_vc_authorization` in `chia/wallet/vc_wallet/vc_wallet.py` executes a path where make `add_vc_authorization` accept stale VC proof or record state after the credential moved on, violating the invariant that old VC proof or record state must not remain authorizing after a later state transition and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/vc_wallet.py:404 `VCWallet.add_vc_authorization`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_vc_authorization`
- Attacker controls: stale VC records or proof context replayed after state transitions
- Exploit idea: make `add_vc_authorization` accept stale VC proof or record state after the credential moved on
- Invariant to test: old VC proof or record state must not remain authorizing after a later state transition
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale VC state into `chia/wallet/vc_wallet/vc_wallet.py:add_vc_authorization` after a later transition and assert no proof or spend path still accepts it
