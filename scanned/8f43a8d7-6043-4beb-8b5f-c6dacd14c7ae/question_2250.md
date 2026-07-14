# Q2250: create_new_did_wallet_from_recovery accepts a DID recovery or transfer path with attacker-controlled lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_new_did_wallet_from_recovery` and control backup, recovery, transfer, and parent-lineage inputs so that `DIDWallet.create_new_did_wallet_from_recovery` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `create_new_did_wallet_from_recovery` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority, violating the invariant that DID recovery and transfer authority must derive from the live singleton lineage only and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:140 `DIDWallet.create_new_did_wallet_from_recovery`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_new_did_wallet_from_recovery`
- Attacker controls: backup, recovery, transfer, and parent-lineage inputs
- Exploit idea: make `create_new_did_wallet_from_recovery` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority
- Invariant to test: DID recovery and transfer authority must derive from the live singleton lineage only
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: replay attacker-crafted DID backup or recovery material into `chia/wallet/did_wallet/did_wallet.py:create_new_did_wallet_from_recovery` and assert recovery fails without live authority
