# Q141: setup_process_global_state authorizes signing or key use for the wrong target

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `setup_process_global_state` and control fingerprints, wallet ids, signing targets, and serialized signing instructions so that `WebSocketServer.setup_process_global_state` in `chia/daemon/server.py` executes a path where make `setup_process_global_state` sign for, unlock, or select a target that differs from the caller's intended or authorized object, violating the invariant that public routes must not authorize key use, signing, or unlock actions for the wrong target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:245 `WebSocketServer.setup_process_global_state`
- Entrypoint: daemon WebSocket command path reaching `setup_process_global_state`
- Attacker controls: fingerprints, wallet ids, signing targets, and serialized signing instructions
- Exploit idea: make `setup_process_global_state` sign for, unlock, or select a target that differs from the caller's intended or authorized object
- Invariant to test: public routes must not authorize key use, signing, or unlock actions for the wrong target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: attempt cross-fingerprint or cross-wallet signing through `chia/daemon/server.py:setup_process_global_state` and assert the selected key target cannot drift
