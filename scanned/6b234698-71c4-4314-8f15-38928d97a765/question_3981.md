# Q3981: handle_did treats attacker-crafted DID spends as authorized state transitions

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `handle_did` and control message spends, metadata updates, and current-coin references so that `WalletStateManager.handle_did` in `chia/wallet/wallet_state_manager.py` executes a path where make `handle_did` accept a DID spend or metadata action that is disconnected from the live singleton lineage, violating the invariant that DID message and metadata spends must not bypass current ownership or lineage checks and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/wallet_state_manager.py:1365 `WalletStateManager.handle_did`
- Entrypoint: wallet RPC or wallet sync flow reaching `handle_did`
- Attacker controls: message spends, metadata updates, and current-coin references
- Exploit idea: make `handle_did` accept a DID spend or metadata action that is disconnected from the live singleton lineage
- Invariant to test: DID message and metadata spends must not bypass current ownership or lineage checks
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: submit DID spend/message edge cases to `chia/wallet/wallet_state_manager.py:handle_did` and assert current-coin and lineage checks gate every state mutation
