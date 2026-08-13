# Q1858: seed signer derivation scope expansion via createSeedBasedTransactionSigner

## Question
Can an unprivileged attacker reach `createSeedBasedTransactionSigner` in `features/tx-signer/src/module/seed-signer.ts` through signTransaction request from a connected website or wallet-integrated app and supply crafted `walletAccount`, `assetName`, and `seedId` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Direct theft of user funds`?

## Target
- File/function: features/tx-signer/src/module/seed-signer.ts::createSeedBasedTransactionSigner
- Entrypoint: signTransaction request from a connected website or wallet-integrated app
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
