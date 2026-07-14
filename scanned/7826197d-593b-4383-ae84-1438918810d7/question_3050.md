# Q3050: create_new_cat_wallet revokes or spends VC state with stale authorization context

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_cat_wallet` and control launcher ids, revocation inputs, and authorization context so that `CRCATWallet.create_new_cat_wallet` in `chia/wallet/vc_wallet/cr_cat_wallet.py` executes a path where make `create_new_cat_wallet` revoke or spend VC state using stale or cross-context authority, violating the invariant that VC revoke or spend authority must not survive stale or swapped authorization context and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/vc_wallet/cr_cat_wallet.py:83 `CRCATWallet.create_new_cat_wallet`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_cat_wallet`
- Attacker controls: launcher ids, revocation inputs, and authorization context
- Exploit idea: make `create_new_cat_wallet` revoke or spend VC state using stale or cross-context authority
- Invariant to test: VC revoke or spend authority must not survive stale or swapped authorization context
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: exercise stale authorization context against `chia/wallet/vc_wallet/cr_cat_wallet.py:create_new_cat_wallet` and assert VC revoke/spend cannot cross credential state boundaries
