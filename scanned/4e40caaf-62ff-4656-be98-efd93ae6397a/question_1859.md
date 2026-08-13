# Q1859: seed signer external key rebinding via signTransaction

## Question
Can an unprivileged attacker reach `signTransaction` in `features/tx-signer/src/module/seed-signer.ts` through signTransaction request from a connected website or wallet-integrated app and supply crafted `assetName`, `seedId`, and `unsignedTx` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/tx-signer/src/module/seed-signer.ts::signTransaction
- Entrypoint: signTransaction request from a connected website or wallet-integrated app
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
