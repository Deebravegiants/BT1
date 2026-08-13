# Q3921: internal cross-wallet decrypt reuse via set

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `port`, `port`, and persisted-state layout so that `set` in `adapters/storage-unsafe-desktop/src/internal.js` leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration, violating the invariant that legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-unsafe-desktop/src/internal.js::set
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a persisted encrypted blob, legacy storage value, and wallet startup / restore timing
- Exploit idea: leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration
- Invariant to test: legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: fuzz legacy and fallback deserialization with crafted metadata and assert integrity checks reject cross-context or downgraded state
