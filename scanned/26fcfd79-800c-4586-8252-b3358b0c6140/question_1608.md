# Q1608: schemas cross-account signing via schemas

## Question
Can an unprivileged attacker reach `schemas` in `features/cached-sodium-encryptor/module/schemas.ts` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `params`, `port`, and `seedId` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/cached-sodium-encryptor/module/schemas.ts::schemas
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
