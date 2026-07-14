# Q3181: launch_new_vc binds VC proofs to the wrong provider or root

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `launch_new_vc` and control provider ids, proof roots, key sets, and VC state transitions so that `VCWallet.launch_new_vc` in `chia/wallet/vc_wallet/vc_wallet.py` executes a path where make `launch_new_vc` bind VC proofs to the wrong provider, proof root, or credential state, violating the invariant that VC proofs must bind to the exact provider, root, and credential state being spent or verified and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/vc_wallet.py:153 `VCWallet.launch_new_vc`
- Entrypoint: wallet RPC or wallet sync flow reaching `launch_new_vc`
- Attacker controls: provider ids, proof roots, key sets, and VC state transitions
- Exploit idea: make `launch_new_vc` bind VC proofs to the wrong provider, proof root, or credential state
- Invariant to test: VC proofs must bind to the exact provider, root, and credential state being spent or verified
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: swap provider ids or proof roots in a local VC test around `chia/wallet/vc_wallet/vc_wallet.py:launch_new_vc` and assert verification and spend paths reject them
