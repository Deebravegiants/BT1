# Q3153: add_vc_proofs reuses stale VC state across proof or spend flows

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_vc_proofs` and control stale VC records or proof context replayed after state transitions so that `VCStore.add_vc_proofs` in `chia/wallet/vc_wallet/vc_store.py` executes a path where make `add_vc_proofs` accept stale VC proof or record state after the credential moved on, violating the invariant that old VC proof or record state must not remain authorizing after a later state transition and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/vc_store.py:246 `VCStore.add_vc_proofs`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_vc_proofs`
- Attacker controls: stale VC records or proof context replayed after state transitions
- Exploit idea: make `add_vc_proofs` accept stale VC proof or record state after the credential moved on
- Invariant to test: old VC proof or record state must not remain authorizing after a later state transition
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale VC state into `chia/wallet/vc_wallet/vc_store.py:add_vc_proofs` after a later transition and assert no proof or spend path still accepts it
