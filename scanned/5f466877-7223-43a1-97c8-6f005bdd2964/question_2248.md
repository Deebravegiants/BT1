# Q2248: create_new_did_wallet accepts stale DID lineage in a live authority path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_did_wallet` and control stale DID parent or lineage state replayed into a live DID path so that `DIDWallet.create_new_did_wallet` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `create_new_did_wallet` accept stale DID lineage or parent state during a live authority transition, violating the invariant that stale DID parent or lineage state must not authorize live DID actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:73 `DIDWallet.create_new_did_wallet`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_did_wallet`
- Attacker controls: stale DID parent or lineage state replayed into a live DID path
- Exploit idea: make `create_new_did_wallet` accept stale DID lineage or parent state during a live authority transition
- Invariant to test: stale DID parent or lineage state must not authorize live DID actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: feed stale parent or lineage data into `chia/wallet/did_wallet/did_wallet.py:create_new_did_wallet` during a live DID update and assert no authority bypass occurs
