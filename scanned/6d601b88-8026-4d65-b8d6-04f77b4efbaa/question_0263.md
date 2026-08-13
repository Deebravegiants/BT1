# Q263: unlock encrypted storage legacy-storage trust confusion via decrypt

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `seedId`, `port`, and persisted-state layout so that `decrypt` in `sdks/headless/src/unlock-encrypted-storage.js` accept a crafted migration payload that downgrades confidentiality or integrity checks, violating the invariant that storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state, and leading to `Direct theft of user funds`?

## Target
- File/function: sdks/headless/src/unlock-encrypted-storage.js::decrypt
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: cross-account restore or seed-rotation timing around encrypted storage reuse
- Exploit idea: accept a crafted migration payload that downgrades confidentiality or integrity checks
- Invariant to test: storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: lock and clear after decrypting storage, then inspect the follow-up restore path to ensure plaintext or cached decryptions are gone
