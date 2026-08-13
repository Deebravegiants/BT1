# Q1637: errors payload-view mismatch via UnsupportedWalletAccountSource

## Question
Can an unprivileged attacker reach `UnsupportedWalletAccountSource` in `features/message-signer/src/module/errors.ts` through signMessage / signIn request from a connected website and supply crafted `account`, `port`, and `account` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Direct theft of user funds`?

## Target
- File/function: features/message-signer/src/module/errors.ts::UnsupportedWalletAccountSource
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
