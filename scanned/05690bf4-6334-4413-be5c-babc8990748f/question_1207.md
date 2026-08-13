# Q1207: secp256k1 cross-account signing via signBuffer

## Question
Can an unprivileged attacker reach `signBuffer` in `features/keychain/module/crypto/secp256k1.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `signature`, `seedId`, and `privateKey` values that reuse cached decrypted material or exported key state across a lock, clear, or account boundary, violating the invariant that derivation scope must never expand beyond the exact approved path or account context, and causing `Direct theft of user funds`?

## Target
- File/function: features/keychain/module/crypto/secp256k1.js::signBuffer
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: the requested wallet account, derivation path, key identifier, and signing payload bytes
- Exploit idea: reuse cached decrypted material or exported key state across a lock, clear, or account boundary
- Invariant to test: derivation scope must never expand beyond the exact approved path or account context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
