# Q869: create signer cross-account signing via getPublicKey

## Question
Can an unprivileged attacker reach `getPublicKey` in `features/keychain/module/create-signer.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `port`, `signature`, and `seedId` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/keychain/module/create-signer.js::getPublicKey
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
