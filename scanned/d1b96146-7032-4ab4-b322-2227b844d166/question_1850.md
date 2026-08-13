# Q1850: seed signer payload-view mismatch via getPublicKey

## Question
Can an unprivileged attacker reach `getPublicKey` in `features/tx-signer/src/module/seed-signer.ts` through signTransaction request from a connected website or wallet-integrated app and supply crafted `assetName`, `seedId`, and `unsignedTx` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Direct theft of user funds`?

## Target
- File/function: features/tx-signer/src/module/seed-signer.ts::getPublicKey
- Entrypoint: signTransaction request from a connected website or wallet-integrated app
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
