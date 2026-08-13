# Q3717: storage migration integrity downgrade via createStorageEncrypted

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `name`, `port`, and persisted-state layout so that `createStorageEncrypted` in `adapters/storage-encrypted/src/storage.ts` use path, namespace, or metadata confusion to overwrite or read a different wallet's persisted state, violating the invariant that encrypted wallet material must be bound to the right seed, namespace, and account context, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-encrypted/src/storage.ts::createStorageEncrypted
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: serialized wallet state fields plus a lock / unlock / clear sequence
- Exploit idea: use path, namespace, or metadata confusion to overwrite or read a different wallet's persisted state
- Invariant to test: encrypted wallet material must be bound to the right seed, namespace, and account context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: unit-test path and namespace collisions and verify one wallet instance cannot overwrite or read another instance's state
