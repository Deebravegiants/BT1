# Q1601: schemas external key rebinding via schemas

## Question
Can an unprivileged attacker reach `schemas` in `features/cached-sodium-encryptor/module/schemas.ts` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `port`, `seedId`, and `keyIdentifier` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Direct theft of user funds`?

## Target
- File/function: features/cached-sodium-encryptor/module/schemas.ts::schemas
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
