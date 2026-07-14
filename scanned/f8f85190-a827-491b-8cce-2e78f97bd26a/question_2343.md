# Q2343: generate_signed_transaction treats attacker-crafted DID spends as authorized state transitions

## Question
Can an unprivileged attacker reach wallet RPC or wallet sync flow reaching `generate_signed_transaction` and control message spends, metadata updates, and current-coin references so that `DIDWallet.generate_signed_transaction` in `chia/wallet/did_wallet/did_wallet.py` executes a path where make `generate_signed_transaction` accept a DID spend or metadata action that is disconnected from the live singleton lineage, violating the invariant that DID message and metadata spends must not bypass current ownership or lineage checks and leading to Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions?

## Target
- File/function: chia/wallet/did_wallet/did_wallet.py:1175 `DIDWallet.generate_signed_transaction`
- Entrypoint: wallet RPC or wallet sync flow reaching `generate_signed_transaction`
- Attacker controls: message spends, metadata updates, and current-coin references
- Exploit idea: make `generate_signed_transaction` accept a DID spend or metadata action that is disconnected from the live singleton lineage
- Invariant to test: DID message and metadata spends must not bypass current ownership or lineage checks
- Expected Immunefi impact: Bypass of wallet, daemon, keychain, RPC, pool, or Data Layer authorization that enables unauthorized signing, key use, coin control, payout redirection, singleton mutation, or protected state transitions
- Fast validation: submit DID spend/message edge cases to `chia/wallet/did_wallet/did_wallet.py:generate_signed_transaction` and assert current-coin and lineage checks gate every state mutation
