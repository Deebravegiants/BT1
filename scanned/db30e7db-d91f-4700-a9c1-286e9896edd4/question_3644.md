# Q3644: index plaintext residue after lock via getSecret

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `port`, `port`, and persisted-state layout so that `getSecret` in `adapters/keystore-mobile/src/index.js` bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted, violating the invariant that lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/keystore-mobile/src/index.js::getSecret
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a crafted import or migration payload that the wallet accepts as prior state
- Exploit idea: bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted
- Invariant to test: lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: fuzz legacy and fallback deserialization with crafted metadata and assert integrity checks reject cross-context or downgraded state
