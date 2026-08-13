# Q197: index external key rebinding via cachedSodiumEncryptorRpc

## Question
Can an unprivileged attacker reach `cachedSodiumEncryptorRpc` in `sdks/headless/src/features/cached-sodium-encryptor-rpc/index.js` through wallet RPC call that asks the SDK to decrypt or unlock persisted wallet material and supply crafted `port`, `port`, and `port` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Direct theft of user funds`?

## Target
- File/function: sdks/headless/src/features/cached-sodium-encryptor-rpc/index.js::cachedSodiumEncryptorRpc
- Entrypoint: wallet RPC call that asks the SDK to decrypt or unlock persisted wallet material
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
