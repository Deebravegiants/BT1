# Q1350: new_signage_point authorizes signing or key use for the wrong target

## Question
Can an unprivileged attacker reach full node mempool, sync, or peer flow reaching `new_signage_point` and control fingerprints, wallet ids, signing targets, and serialized signing instructions so that `FullNodeStore.new_signage_point` in `chia/full_node/full_node_store.py` executes a path where make `new_signage_point` sign for, unlock, or select a target that differs from the caller's intended or authorized object, violating the invariant that public routes must not authorize key use, signing, or unlock actions for the wrong target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_store.py:709 `FullNodeStore.new_signage_point`
- Entrypoint: full node mempool, sync, or peer flow reaching `new_signage_point`
- Attacker controls: fingerprints, wallet ids, signing targets, and serialized signing instructions
- Exploit idea: make `new_signage_point` sign for, unlock, or select a target that differs from the caller's intended or authorized object
- Invariant to test: public routes must not authorize key use, signing, or unlock actions for the wrong target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: attempt cross-fingerprint or cross-wallet signing through `chia/full_node/full_node_store.py:new_signage_point` and assert the selected key target cannot drift
