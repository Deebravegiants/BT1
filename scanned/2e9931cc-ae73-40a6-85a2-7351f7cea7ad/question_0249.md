# Q249: unlock encrypted storage cross-wallet decrypt reuse via createUnlockEncryptedStorage

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `seedId`, `port`, and persisted-state layout so that `createUnlockEncryptedStorage` in `sdks/headless/src/unlock-encrypted-storage.js` leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration, violating the invariant that legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path, and leading to `Direct theft of user funds`?

## Target
- File/function: sdks/headless/src/unlock-encrypted-storage.js::createUnlockEncryptedStorage
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a persisted encrypted blob, legacy storage value, and wallet startup / restore timing
- Exploit idea: leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration
- Invariant to test: legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test path and namespace collisions and verify one wallet instance cannot overwrite or read another instance's state
