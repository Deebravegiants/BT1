# Q3900: storage legacy-storage trust confusion via delete

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `name`, `port`, and persisted-state layout so that `delete` in `adapters/storage-mobile/src/storage.ts` accept a crafted migration payload that downgrades confidentiality or integrity checks, violating the invariant that storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-mobile/src/storage.ts::delete
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: cross-account restore or seed-rotation timing around encrypted storage reuse
- Exploit idea: accept a crafted migration payload that downgrades confidentiality or integrity checks
- Invariant to test: storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test path and namespace collisions and verify one wallet instance cannot overwrite or read another instance's state
