# Q1106: cardano payload-view mismatch via seedToCardanoV1Seed

## Question
Can an unprivileged attacker reach `seedToCardanoV1Seed` in `features/keychain/module/crypto/cardano.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `seedId`, `privateKey`, and `publicKey` values that trick the signing path into validating one payload view while signing another payload semantics, violating the invariant that externally supplied key material must never inherit trust or authorization from a different account context, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/keychain/module/crypto/cardano.js::seedToCardanoV1Seed
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: a chain-specific signing request whose visible fields differ from the actually signed bytes
- Exploit idea: trick the signing path into validating one payload view while signing another payload semantics
- Invariant to test: externally supplied key material must never inherit trust or authorization from a different account context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
