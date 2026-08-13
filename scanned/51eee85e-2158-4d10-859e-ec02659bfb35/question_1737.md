# Q1737: seed signer payload-view mismatch via #getKeyId

## Question
Can an unprivileged attacker reach `#getKeyId` in `features/message-signer/src/module/seed-signer.ts` through signMessage / signIn request from a connected website and supply crafted `signature`, `account`, and `walletAccount` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Direct theft of user funds`?

## Target
- File/function: features/message-signer/src/module/seed-signer.ts::#getKeyId
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
