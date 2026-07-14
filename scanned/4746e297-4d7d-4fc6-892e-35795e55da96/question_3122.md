# Q3122: solve_did_tp accepts a DID recovery or transfer path with attacker-controlled lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `solve_did_tp` and control backup, recovery, transfer, and parent-lineage inputs so that `solve_did_tp` in `chia/wallet/vc_wallet/vc_drivers.py` executes a path where make `solve_did_tp` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority, violating the invariant that DID recovery and transfer authority must derive from the live singleton lineage only and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/vc_wallet/vc_drivers.py:162 `solve_did_tp`
- Entrypoint: wallet RPC or wallet sync flow reaching `solve_did_tp`
- Attacker controls: backup, recovery, transfer, and parent-lineage inputs
- Exploit idea: make `solve_did_tp` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority
- Invariant to test: DID recovery and transfer authority must derive from the live singleton lineage only
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: replay attacker-crafted DID backup or recovery material into `chia/wallet/vc_wallet/vc_drivers.py:solve_did_tp` and assert recovery fails without live authority
