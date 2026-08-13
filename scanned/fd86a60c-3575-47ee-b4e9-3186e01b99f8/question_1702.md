# Q1702: message signer payload-view mismatch via MessageSigner

## Question
Can an unprivileged attacker reach `MessageSigner` in `features/message-signer/src/module/message-signer.ts` through signMessage / signIn request from a connected website and supply crafted `account`, `walletAccount`, and `name` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/message-signer/src/module/message-signer.ts::MessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: construct a payload whose displayed fields and serialized bytes can diverge and assert the signer rejects or canonicalizes it safely
