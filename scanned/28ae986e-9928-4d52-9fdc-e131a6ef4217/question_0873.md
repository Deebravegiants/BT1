# Q873: create signer payload-view mismatch via getPublicKey

## Question
Can an unprivileged attacker reach `getPublicKey` in `features/keychain/module/create-signer.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `port`, `signature`, and `seedId` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/keychain/module/create-signer.js::getPublicKey
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
