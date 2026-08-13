# Q1350: sodium external key rebinding via createEncryptor

## Question
Can an unprivileged attacker reach `createEncryptor` in `features/keychain/module/crypto/sodium.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `seedId`, `privateKey`, and `publicKey` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/keychain/module/crypto/sodium.js::createEncryptor
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
