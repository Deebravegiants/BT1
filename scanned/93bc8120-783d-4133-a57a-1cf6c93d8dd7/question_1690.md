# Q1690: hardware signer derivation scope expansion via createHardwareMessageSigner

## Question
Can an unprivileged attacker reach `createHardwareMessageSigner` in `features/message-signer/src/module/hardware-signer.ts` through signMessage / signIn request from a connected website and supply crafted `message`, `account`, and `walletAccount` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/message-signer/src/module/hardware-signer.ts::createHardwareMessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
