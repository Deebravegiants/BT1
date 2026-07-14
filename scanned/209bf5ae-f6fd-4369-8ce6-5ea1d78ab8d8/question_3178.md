# Q3178: remove_coin revokes or spends VC state with stale authorization context

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `remove_coin` and control launcher ids, revocation inputs, and authorization context so that `VCWallet.remove_coin` in `chia/wallet/vc_wallet/vc_wallet.py` executes a path where make `remove_coin` revoke or spend VC state using stale or cross-context authority, violating the invariant that VC revoke or spend authority must not survive stale or swapped authorization context and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/vc_wallet/vc_wallet.py:130 `VCWallet.remove_coin`
- Entrypoint: wallet RPC or wallet sync flow reaching `remove_coin`
- Attacker controls: launcher ids, revocation inputs, and authorization context
- Exploit idea: make `remove_coin` revoke or spend VC state using stale or cross-context authority
- Invariant to test: VC revoke or spend authority must not survive stale or swapped authorization context
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: exercise stale authorization context against `chia/wallet/vc_wallet/vc_wallet.py:remove_coin` and assert VC revoke/spend cannot cross credential state boundaries
