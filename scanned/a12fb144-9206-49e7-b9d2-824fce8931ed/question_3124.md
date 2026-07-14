# Q3124: solve_did_tp accepts stale DID lineage in a live authority path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `solve_did_tp` and control stale DID parent or lineage state replayed into a live DID path so that `solve_did_tp` in `chia/wallet/vc_wallet/vc_drivers.py` executes a path where make `solve_did_tp` accept stale DID lineage or parent state during a live authority transition, violating the invariant that stale DID parent or lineage state must not authorize live DID actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/vc_wallet/vc_drivers.py:162 `solve_did_tp`
- Entrypoint: wallet RPC or wallet sync flow reaching `solve_did_tp`
- Attacker controls: stale DID parent or lineage state replayed into a live DID path
- Exploit idea: make `solve_did_tp` accept stale DID lineage or parent state during a live authority transition
- Invariant to test: stale DID parent or lineage state must not authorize live DID actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: feed stale parent or lineage data into `chia/wallet/vc_wallet/vc_drivers.py:solve_did_tp` during a live DID update and assert no authority bypass occurs
