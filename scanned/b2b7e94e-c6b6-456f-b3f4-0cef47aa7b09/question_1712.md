# Q1712: message signer payload-view mismatch via MessageSigner

## Question
Can an unprivileged attacker reach `MessageSigner` in `features/message-signer/src/module/message-signer.ts` through signMessage / signIn request from a connected website and supply crafted `account`, `walletAccount`, and `name` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/message-signer/src/module/message-signer.ts::MessageSigner
- Entrypoint: signMessage / signIn request from a connected website
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
