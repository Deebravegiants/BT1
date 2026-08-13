# Q1074: cardano derivation scope expansion via getCardanoV1ExtendedPublicKey

## Question
Can an unprivileged attacker reach `getCardanoV1ExtendedPublicKey` in `features/keychain/module/crypto/cardano.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `message`, `signature`, and `seedId` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Sitewide disruption of core services`?

## Target
- File/function: features/keychain/module/crypto/cardano.js::getCardanoV1ExtendedPublicKey
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: lock and clear between repeated export/sign operations and verify no cached key material remains usable
