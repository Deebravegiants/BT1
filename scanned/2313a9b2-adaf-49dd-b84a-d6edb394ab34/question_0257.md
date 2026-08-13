# Q257: unlock encrypted storage plaintext residue after lock via decrypt

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `seedId`, `port`, and persisted-state layout so that `decrypt` in `sdks/headless/src/unlock-encrypted-storage.js` bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted, violating the invariant that lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind, and leading to `Direct theft of user funds`?

## Target
- File/function: sdks/headless/src/unlock-encrypted-storage.js::decrypt
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: a crafted import or migration payload that the wallet accepts as prior state
- Exploit idea: bind legacy or fallback storage to the wrong key namespace so attacker-chosen state is trusted
- Invariant to test: lock, clear, import, and migration must not leave reusable decrypted or plaintext state behind
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test path and namespace collisions and verify one wallet instance cannot overwrite or read another instance's state
