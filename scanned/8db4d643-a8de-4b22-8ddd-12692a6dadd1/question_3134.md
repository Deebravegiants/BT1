# Q3134: add_or_replace_vc_record revokes or spends VC state with stale authorization context

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `add_or_replace_vc_record` and control launcher ids, revocation inputs, and authorization context so that `VCStore.add_or_replace_vc_record` in `chia/wallet/vc_wallet/vc_store.py` executes a path where make `add_or_replace_vc_record` revoke or spend VC state using stale or cross-context authority, violating the invariant that VC revoke or spend authority must not survive stale or swapped authorization context and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/vc_wallet/vc_store.py:154 `VCStore.add_or_replace_vc_record`
- Entrypoint: wallet RPC or wallet sync flow reaching `add_or_replace_vc_record`
- Attacker controls: launcher ids, revocation inputs, and authorization context
- Exploit idea: make `add_or_replace_vc_record` revoke or spend VC state using stale or cross-context authority
- Invariant to test: VC revoke or spend authority must not survive stale or swapped authorization context
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: exercise stale authorization context against `chia/wallet/vc_wallet/vc_store.py:add_or_replace_vc_record` and assert VC revoke/spend cannot cross credential state boundaries
