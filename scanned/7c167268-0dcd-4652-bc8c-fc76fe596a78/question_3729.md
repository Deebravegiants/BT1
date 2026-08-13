# Q3729: with filesystem fallback plaintext residue after lock via clear

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `origin`, `name`, and persisted-state layout so that `clear` in `adapters/storage-mobile/src/helpers/with-filesystem-fallback.ts` bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted, violating the invariant that lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-mobile/src/helpers/with-filesystem-fallback.ts::clear
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a crafted import or migration payload that the wallet accepts as prior state
- Exploit idea: bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted
- Invariant to test: lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: prepare two wallet contexts, persist state in one, then restore or migrate the other and assert ciphertext, metadata, and namespaces never cross-decrypt or cross-load
