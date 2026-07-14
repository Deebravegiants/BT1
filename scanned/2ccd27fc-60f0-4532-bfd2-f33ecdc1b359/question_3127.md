# Q3127: solve_did_tp reuses stale VC state across proof or spend flows

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `solve_did_tp` and control stale VC records or proof context replayed after state transitions so that `solve_did_tp` in `chia/wallet/vc_wallet/vc_drivers.py` executes a path where make `solve_did_tp` accept stale VC proof or record state after the credential moved on, violating the invariant that old VC proof or record state must not remain authorizing after a later state transition and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/vc_drivers.py:162 `solve_did_tp`
- Entrypoint: wallet RPC or wallet sync flow reaching `solve_did_tp`
- Attacker controls: stale VC records or proof context replayed after state transitions
- Exploit idea: make `solve_did_tp` accept stale VC proof or record state after the credential moved on
- Invariant to test: old VC proof or record state must not remain authorizing after a later state transition
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: replay stale VC state into `chia/wallet/vc_wallet/vc_drivers.py:solve_did_tp` after a later transition and assert no proof or spend path still accepts it
