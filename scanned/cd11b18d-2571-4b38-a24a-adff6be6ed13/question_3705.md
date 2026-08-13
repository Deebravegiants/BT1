# Q3705: storage legacy-storage trust confusion via batchGet

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `name`, `port`, and persisted-state layout so that `batchGet` in `adapters/storage-encrypted/src/storage.ts` accept a crafted migration payload that downgrades confidentiality or integrity checks, violating the invariant that storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-encrypted/src/storage.ts::batchGet
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: cross-account restore or seed-rotation timing around encrypted storage reuse
- Exploit idea: accept a crafted migration payload that downgrades confidentiality or integrity checks
- Invariant to test: storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test path and namespace collisions and verify one wallet instance cannot overwrite or read another instance's state
