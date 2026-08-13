# Q3691: storage cross-wallet decrypt reuse via isDecryptionError

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `port`, `message`, and persisted-state layout so that `isDecryptionError` in `adapters/storage-encrypted/src/storage.ts` leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration, violating the invariant that legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-encrypted/src/storage.ts::isDecryptionError
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a persisted encrypted blob, legacy storage value, and wallet startup / restore timing
- Exploit idea: leave decrypted or plaintext-adjacent state behind after lock, clear, import, or migration
- Invariant to test: legacy and fallback storage paths must preserve the same confidentiality and integrity guarantees as the primary path
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: lock and clear after decrypting storage, then inspect the follow-up restore path to ensure plaintext or cached decryptions are gone
