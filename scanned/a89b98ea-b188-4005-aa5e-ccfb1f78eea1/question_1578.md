# Q1578: cached sodium encryptor cross-account signing via createCachedSodiumEncryptor

## Question
Can an unprivileged attacker reach `createCachedSodiumEncryptor` in `features/cached-sodium-encryptor/module/cached-sodium-encryptor.ts` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `seedId`, `privateKey`, and `params` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/cached-sodium-encryptor/module/cached-sodium-encryptor.ts::createCachedSodiumEncryptor
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
