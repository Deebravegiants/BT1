# Q1661: hardware signer external key rebinding via HardwareMessageSigner

## Question
Can an unprivileged attacker reach `HardwareMessageSigner` in `features/message-signer/src/module/hardware-signer.ts` through signMessage / signIn request from a connected website and supply crafted `account`, `walletAccount`, and `assetName` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Direct theft of user funds`?

## Target
- File/function: features/message-signer/src/module/hardware-signer.ts::HardwareMessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
