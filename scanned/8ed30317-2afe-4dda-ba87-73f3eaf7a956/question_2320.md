# Q2320: generate_eve_spend accepts a DID recovery or transfer path with attacker-controlled lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_eve_spend` and control backup, recovery, transfer, and parent-lineage inputs so that `DIDWallet.generate_eve_spend` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `generate_eve_spend` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority, violating the invariant that DID recovery and transfer authority must derive from the live singleton lineage only and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:997 `DIDWallet.generate_eve_spend`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_eve_spend`
- Attacker controls: backup, recovery, transfer, and parent-lineage inputs
- Exploit idea: make `generate_eve_spend` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority
- Invariant to test: DID recovery and transfer authority must derive from the live singleton lineage only
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: replay attacker-crafted DID backup or recovery material into `chia/wallet/did_wallet/did_wallet.py:generate_eve_spend` and assert recovery fails without live authority
