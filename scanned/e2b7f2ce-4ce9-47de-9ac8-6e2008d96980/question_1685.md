# Q1685: hardware signer derivation scope expansion via HardwareMessageSigner

## Question
Can an unprivileged attacker reach `HardwareMessageSigner` in `features/message-signer/src/module/hardware-signer.ts` through signMessage / signIn request from a connected website and supply crafted `account`, `walletAccount`, and `assetName` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Direct theft of user funds`?

## Target
- File/function: features/message-signer/src/module/hardware-signer.ts::HardwareMessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
