# Q3660: get_private_key authorizes signing or key use for the wrong target

## Question
Can an unprivileged attacker reach RPC route `get_private_key` and control fingerprints, wallet ids, signing targets, and serialized signing instructions so that `WalletRpcApi.get_private_key` in `chia/wallet/wallet_rpc_api.py` executes a path where make `get_private_key` sign for, unlock, or select a target that differs from the caller's intended or authorized object, violating the invariant that public routes must not authorize key use, signing, or unlock actions for the wrong target and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_rpc_api.py:807 `WalletRpcApi.get_private_key`
- Entrypoint: RPC route `get_private_key`
- Attacker controls: fingerprints, wallet ids, signing targets, and serialized signing instructions
- Exploit idea: make `get_private_key` sign for, unlock, or select a target that differs from the caller's intended or authorized object
- Invariant to test: public routes must not authorize key use, signing, or unlock actions for the wrong target
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: attempt cross-fingerprint or cross-wallet signing through `chia/wallet/wallet_rpc_api.py:get_private_key` and assert the selected key target cannot drift
