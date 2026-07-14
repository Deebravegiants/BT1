# Q1069: signed_values authorizes signing or key use for the wrong target

## Question
Can an unprivileged attacker reach P2P message handler `signed_values` and control fingerprints, wallet ids, signing targets, and serialized signing instructions so that `FullNodeAPI.signed_values` in `chia/full_node/full_node_api.py` executes a path where make `signed_values` sign for, unlock, or select a target that differs from the caller's intended or authorized object, violating the invariant that public routes must not authorize key use, signing, or unlock actions for the wrong target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/full_node/full_node_api.py:1225 `FullNodeAPI.signed_values`
- Entrypoint: P2P message handler `signed_values`
- Attacker controls: fingerprints, wallet ids, signing targets, and serialized signing instructions
- Exploit idea: make `signed_values` sign for, unlock, or select a target that differs from the caller's intended or authorized object
- Invariant to test: public routes must not authorize key use, signing, or unlock actions for the wrong target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: attempt cross-fingerprint or cross-wallet signing through `chia/full_node/full_node_api.py:signed_values` and assert the selected key target cannot drift
