# Q3718: storage namespace collision via isDecryptionError

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `port`, `message`, and persisted-state layout so that `isDecryptionError` in `adapters/storage-encrypted/src/storage.ts` make secrets encrypted for one seed, account, or namespace decrypt or deserialize under another context, violating the invariant that serialized metadata and content must be authenticated before cross-session or cross-account reuse, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-encrypted/src/storage.ts::isDecryptionError
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: namespace, key ID, or storage-path choices that are reachable from normal wallet usage
- Exploit idea: make secrets encrypted for one seed, account, or namespace decrypt or deserialize under another context
- Invariant to test: serialized metadata and content must be authenticated before cross-session or cross-account reuse
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: fuzz legacy and fallback deserialization with crafted metadata and assert integrity checks reject cross-context or downgraded state
