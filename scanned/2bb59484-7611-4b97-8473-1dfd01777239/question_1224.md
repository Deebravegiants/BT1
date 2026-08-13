# Q1224: secp256k1 derivation scope expansion via createSigner

## Question
Can an unprivileged attacker reach `createSigner` in `features/keychain/module/crypto/secp256k1.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `seedId`, `privateKey`, and `port` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/keychain/module/crypto/secp256k1.js::createSigner
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
