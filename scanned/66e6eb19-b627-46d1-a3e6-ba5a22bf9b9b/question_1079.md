# Q1079: cardano derivation scope expansion via seedToCardanoV1Seed

## Question
Can an unprivileged attacker reach `seedToCardanoV1Seed` in `features/keychain/module/crypto/cardano.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `port`, `message`, and `signature` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Direct theft of user funds`?

## Target
- File/function: features/keychain/module/crypto/cardano.js::seedToCardanoV1Seed
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
