# Q1756: seed signer external key rebinding via signMessage

## Question
Can an unprivileged attacker reach `signMessage` in `features/message-signer/src/module/seed-signer.ts` through signMessage / signIn request from a connected website and supply crafted `port`, `message`, and `signature` values that widen a derivation or export scope so a narrower approved request yields broader key material, violating the invariant that locked state must prevent all operations that derive, export, decrypt, or sign with key material, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/message-signer/src/module/seed-signer.ts::signMessage
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: the order of lock/unlock, export, and sign requests around cached decrypted state
- Exploit idea: widen a derivation or export scope so a narrower approved request yields broader key material
- Invariant to test: locked state must prevent all operations that derive, export, decrypt, or sign with key material
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
