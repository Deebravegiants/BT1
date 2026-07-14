# Q3063: create_from_puzzle_info binds VC proofs to the wrong provider or root

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_from_puzzle_info` and control provider ids, proof roots, key sets, and VC state transitions so that `CRCATWallet.create_from_puzzle_info` in `chia/wallet/vc_wallet/cr_cat_wallet.py` executes a path where make `create_from_puzzle_info` bind VC proofs to the wrong provider, proof root, or credential state, violating the invariant that VC proofs must bind to the exact provider, root, and credential state being spent or verified and leading to Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_wallet.py:130 `CRCATWallet.create_from_puzzle_info`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_from_puzzle_info`
- Attacker controls: provider ids, proof roots, key sets, and VC state transitions
- Exploit idea: make `create_from_puzzle_info` bind VC proofs to the wrong provider, proof root, or credential state
- Invariant to test: VC proofs must bind to the exact provider, root, and credential state being spent or verified
- Expected Immunefi impact: Corruption of coin records, lineage, puzzle ownership, offer/trade settlement state, mempool or hint indexes, wallet sync state, pool membership state, or Data Layer root/store state with direct security impact
- Fast validation: swap provider ids or proof roots in a local VC test around `chia/wallet/vc_wallet/cr_cat_wallet.py:create_from_puzzle_info` and assert verification and spend paths reject them
