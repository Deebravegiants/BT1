# Q3998: handle_vc binds VC proofs to the wrong provider or root

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_vc` and control provider ids, proof roots, key sets, and VC state transitions so that `WalletStateManager.handle_vc` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_vc` bind VC proofs to the wrong provider, proof root, or credential state, violating the invariant that VC proofs must bind to the exact provider, root, and credential state being spent or verified and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1745 `WalletStateManager.handle_vc`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_vc`
- Attacker controls: provider ids, proof roots, key sets, and VC state transitions
- Exploit idea: make `handle_vc` bind VC proofs to the wrong provider, proof root, or credential state
- Invariant to test: VC proofs must bind to the exact provider, root, and credential state being spent or verified
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: swap provider ids or proof roots in a local VC test around `chia/wallet/wallet_state_manager.py:handle_vc` and assert verification and spend paths reject them
