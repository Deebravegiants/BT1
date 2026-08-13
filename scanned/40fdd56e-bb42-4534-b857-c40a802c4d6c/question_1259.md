# Q1259: seed id derivation scope expansion via getUniqueSeedIds

## Question
Can an unprivileged attacker reach `getUniqueSeedIds` in `features/keychain/module/crypto/seed-id.js` through signing or key-export flow triggered by a connected dapp or standard wallet action and supply crafted `port`, `seedId`, and `port` values that make the SDK sign with a different seed, key, or wallet account than the user approved, violating the invariant that cached decrypted material must be cleared on lock, clear, and account-boundary changes, and causing `Direct theft of user funds`?

## Target
- File/function: features/keychain/module/crypto/seed-id.js::getUniqueSeedIds
- Entrypoint: signing or key-export flow triggered by a connected dapp or standard wallet action
- Attacker controls: external private-key or seed-adjacent material accepted through a normal signing-related flow
- Exploit idea: make the SDK sign with a different seed, key, or wallet account than the user approved
- Invariant to test: cached decrypted material must be cleared on lock, clear, and account-boundary changes
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test two wallet accounts or seeds, request a sign/export on one, then swap context and assert the result cannot come from the other
