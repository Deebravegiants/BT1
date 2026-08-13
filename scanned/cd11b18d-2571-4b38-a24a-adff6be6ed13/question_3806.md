# Q3806: with filesystem fallback cross-wallet decrypt reuse via clear

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `port`, `origin`, and persisted-state layout so that `clear` in `adapters/storage-mobile/src/helpers/with-filesystem-fallback.ts` leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration, violating the invariant that legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-mobile/src/helpers/with-filesystem-fallback.ts::clear
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a persisted encrypted blob, legacy storage value, and wallet startup / restore timing
- Exploit idea: leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration
- Invariant to test: legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test path and namespace collisions and verify one wallet instance cannot overwrite or read another instance's state
