# Q153: send_all_responses authorizes signing or key use for the wrong target

## Question
Can an unprivileged attacker reach daemon WebSocket command path reaching `send_all_responses` and control fingerprints, wallet ids, signing targets, and serialized signing instructions so that `WebSocketServer.send_all_responses` in `chia/daemon/server.py` executes a path where make `send_all_responses` sign for, unlock, or select a target that differs from the caller's intended or authorized object, violating the invariant that public routes must not authorize key use, signing, or unlock actions for the wrong target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/daemon/server.py:344 `WebSocketServer.send_all_responses`
- Entrypoint: daemon WebSocket command path reaching `send_all_responses`
- Attacker controls: fingerprints, wallet ids, signing targets, and serialized signing instructions
- Exploit idea: make `send_all_responses` sign for, unlock, or select a target that differs from the caller's intended or authorized object
- Invariant to test: public routes must not authorize key use, signing, or unlock actions for the wrong target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: attempt cross-fingerprint or cross-wallet signing through `chia/daemon/server.py:send_all_responses` and assert the selected key target cannot drift
