# Q3123: solve_did_tp treats attacker-crafted DID spends as authorized state transitions

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `solve_did_tp` and control message spends, metadata updates, and current-coin references so that `solve_did_tp` in `chia/wallet/vc_wallet/vc_drivers.py` executes a path where make `solve_did_tp` accept a DID spend or metadata action that is disconnected from the live singleton lineage, violating the invariant that DID message and metadata spends must not bypass current ownership or lineage checks and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/vc_wallet/vc_drivers.py:162 `solve_did_tp`
- Entrypoint: wallet RPC or wallet sync flow reaching `solve_did_tp`
- Attacker controls: message spends, metadata updates, and current-coin references
- Exploit idea: make `solve_did_tp` accept a DID spend or metadata action that is disconnected from the live singleton lineage
- Invariant to test: DID message and metadata spends must not bypass current ownership or lineage checks
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: submit DID spend/message edge cases to `chia/wallet/vc_wallet/vc_drivers.py:solve_did_tp` and assert current-coin and lineage checks gate every state mutation
