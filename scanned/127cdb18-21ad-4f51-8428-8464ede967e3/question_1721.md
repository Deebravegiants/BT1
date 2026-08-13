# Q1721: seed signer external key rebinding via getPublicKey

## Question
Can an unprivileged attacker reach `getPublicKey` in `features/message-signer/src/module/seed-signer.ts` through signMessage / signIn request from a connected website and supply crafted `port`, `message`, and `signature` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Direct theft of user funds`?

## Target
- File/function: features/message-signer/src/module/seed-signer.ts::getPublicKey
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
