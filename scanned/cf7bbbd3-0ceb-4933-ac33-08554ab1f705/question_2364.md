# Q2364: create_spend_for_message accepts a DID recovery or transfer path with attacker-controlled lineage

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `create_spend_for_message` and control backup, recovery, transfer, and parent-lineage inputs so that `create_spend_for_message` in `chia/wallet/did_wallet/did_wallet_puzzles.py` executes a path where make `create_spend_for_message` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority, violating the invariant that DID recovery and transfer authority must derive from the live singleton lineage only and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/did_wallet/did_wallet_puzzles.py:157 `create_spend_for_message`
- Entrypoint: wallet RPC or wallet sync flow reaching `create_spend_for_message`
- Attacker controls: backup, recovery, transfer, and parent-lineage inputs
- Exploit idea: make `create_spend_for_message` treat attacker-controlled recovery or backup material as if it proved legitimate DID authority
- Invariant to test: DID recovery and transfer authority must derive from the live singleton lineage only
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: replay attacker-crafted DID backup or recovery material into `chia/wallet/did_wallet/did_wallet_puzzles.py:create_spend_for_message` and assert recovery fails without live authority
