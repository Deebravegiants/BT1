# Q1865: seed signer payload-view mismatch via signTransaction

## Question
Can an unprivileged attacker reach `signTransaction` in `features/tx-signer/src/module/seed-signer.ts` through signTransaction request from a connected website or wallet-integrated app and supply crafted `signature`, `account`, and `walletAccount` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/tx-signer/src/module/seed-signer.ts::signTransaction
- Entrypoint: signTransaction request from a connected website or wallet-integrated app
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
