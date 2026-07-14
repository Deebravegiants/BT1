# Q3043: spend_many revokes or spends VC state with stale authorization context

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `spend_many` and control launcher ids, revocation inputs, and authorization context so that `CRCAT.spend_many` in `chia/wallet/vc_wallet/cr_cat_drivers.py` executes a path where make `spend_many` revoke or spend VC state using stale or cross-context authority, violating the invariant that VC revoke or spend authority must not survive stale or swapped authorization context and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_drivers.py:515 `CRCAT.spend_many`
- Entrypoint: wallet RPC or wallet sync flow reaching `spend_many`
- Attacker controls: launcher ids, revocation inputs, and authorization context
- Exploit idea: make `spend_many` revoke or spend VC state using stale or cross-context authority
- Invariant to test: VC revoke or spend authority must not survive stale or swapped authorization context
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: exercise stale authorization context against `chia/wallet/vc_wallet/cr_cat_drivers.py:spend_many` and assert VC revoke/spend cannot cross credential state boundaries
