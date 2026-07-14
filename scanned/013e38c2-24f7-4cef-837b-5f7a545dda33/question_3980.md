# Q3980: handle_did accepts a DID recovery or transfer path with attacker-controlled lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_did` and control backup, recovery, transfer, and parent-lineage inputs so that `WalletStateManager.handle_did` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_did` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority, violating the invariant that DID recovery and transfer authority must derive from the live singleton lineage only and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1365 `WalletStateManager.handle_did`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_did`
- Attacker controls: backup, recovery, transfer, and parent-lineage inputs
- Exploit idea: make `handle_did` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority
- Invariant to test: DID recovery and transfer authority must derive from the live singleton lineage only
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: replay attacker-crafted DID backup or recovery material into `chia/wallet/wallet_state_manager.py:handle_did` and assert recovery fails without live authority
