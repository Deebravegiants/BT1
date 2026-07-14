# Q2322: generate_eve_spend accepts stale DID lineage in a live authority path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_eve_spend` and control stale DID parent or lineage state replayed into a live DID path so that `DIDWallet.generate_eve_spend` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `generate_eve_spend` accept stale DID lineage or parent state during a live authority transition, violating the invariant that stale DID parent or lineage state must not authorize live DID actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:997 `DIDWallet.generate_eve_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_eve_spend`
- Attacker controls: stale DID parent or lineage state replayed into a live DID path
- Exploit idea: make `generate_eve_spend` accept stale DID lineage or parent state during a live authority transition
- Invariant to test: stale DID parent or lineage state must not authorize live DID actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: feed stale parent or lineage data into `chia/wallet/did_wallet/did_wallet.py:generate_eve_spend` during a live DID update and assert no authority bypass occurs
