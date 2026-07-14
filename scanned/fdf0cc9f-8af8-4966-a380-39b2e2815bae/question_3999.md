# Q3999: handle_vc revokes or spends VC state with stale authorization context

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_vc` and control launcher ids, revocation inputs, and authorization context so that `WalletStateManager.handle_vc` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_vc` revoke or spend VC state using stale or cross-context authority, violating the invariant that VC revoke or spend authority must not survive stale or swapped authorization context and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1745 `WalletStateManager.handle_vc`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_vc`
- Attacker controls: launcher ids, revocation inputs, and authorization context
- Exploit idea: make `handle_vc` revoke or spend VC state using stale or cross-context authority
- Invariant to test: VC revoke or spend authority must not survive stale or swapped authorization context
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: exercise stale authorization context against `chia/wallet/wallet_state_manager.py:handle_vc` and assert VC revoke/spend cannot cross credential state boundaries
