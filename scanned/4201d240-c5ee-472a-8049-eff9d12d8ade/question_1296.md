# Q1296: sodium payload-view mismatch via createEncryptor

## Question
Can an unprivileged attacker reach `createEncryptor` in `features/keychain/module/crypto/sodium.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `seedId`, `privateKey`, and `publicKey` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/keychain/module/crypto/sodium.js::createEncryptor
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
