# Q3894: storage plaintext residue after lock via batchGet

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `name`, `port`, and persisted-state layout so that `batchGet` in `adapters/storage-mobile/src/storage.ts` bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted, violating the invariant that lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-mobile/src/storage.ts::batchGet
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a crafted import or migration payload that the wallet accepts as prior state
- Exploit idea: bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted
- Invariant to test: lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: lock and clear after decrypting storage, then inspect the follow-up restore path to ensure plaintext or cached decryptions are gone
