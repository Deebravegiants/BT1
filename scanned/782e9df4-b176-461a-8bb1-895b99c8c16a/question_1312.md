# Q1312: sodium cross-account signing via getKeysFromSeed

## Question
Can an unprivileged attacker reach `getKeysFromSeed` in `features/keychain/module/crypto/sodium.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `message`, `signature`, and `seedId` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/keychain/module/crypto/sodium.js::getKeysFromSeed
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
