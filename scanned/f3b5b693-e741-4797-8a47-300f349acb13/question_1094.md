# Q1094: cardano derivation scope expansion via seedToCardanoV1Seed

## Question
Can an unprivileged attacker reach `seedToCardanoV1Seed` in `features/keychain/module/crypto/cardano.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `seedId`, `privateKey`, and `publicKey` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/keychain/module/crypto/cardano.js::seedToCardanoV1Seed
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
