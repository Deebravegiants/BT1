# Q2355: create_recovery_message_puzzle accepts stale DID lineage in a live authority path

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_recovery_message_puzzle` and control stale DID parent or lineage state replayed into a live DID path so that `create_recovery_message_puzzle` in `chia/wallet/did_wallet/did_wallet_puzzles.py` executes a path where make `create_recovery_message_puzzle` accept stale DID lineage or parent state during a live authority transition, violating the invariant that stale DID parent or lineage state must not authorize live DID actions and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/did_wallet/did_wallet_puzzles.py:137 `create_recovery_message_puzzle`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_recovery_message_puzzle`
- Attacker controls: stale DID parent or lineage state replayed into a live DID path
- Exploit idea: make `create_recovery_message_puzzle` accept stale DID lineage or parent state during a live authority transition
- Invariant to test: stale DID parent or lineage state must not authorize live DID actions
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: feed stale parent or lineage data into `chia/wallet/did_wallet/did_wallet_puzzles.py:create_recovery_message_puzzle` during a live DID update and assert no authority bypass occurs
