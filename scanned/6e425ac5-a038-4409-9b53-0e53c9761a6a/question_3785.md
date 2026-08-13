# Q3785: with filesystem fallback legacy-storage trust confusion via delete

## Question
Can an unprivileged attacker trigger wallet import, restore, unlock, or startup path that reads persisted wallet state with attacker-controlled `port`, `origin`, and persisted-state layout so that `delete` in `adapters/storage-mobile/src/helpers/with-filesystem-fallback.ts` accept a crafted migration payload that downgrades confidentiality or integrity checks, violating the invariant that storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state, and leading to `Direct theft of user funds`?

## Target
- File/function: adapters/storage-mobile/src/helpers/with-filesystem-fallback.ts::delete
- Entrypoint: wallet import, restore, unlock, or startup path that reads persisted wallet state
- Attacker controls: cross-account restore or seed-rotation timing around encrypted storage reuse
- Exploit idea: accept a crafted migration payload that downgrades confidentiality or integrity checks
- Invariant to test: storage namespaces and paths must not let one wallet instance read or overwrite another wallet instance's state
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: prepare two wallet contexts, persist state in one, then restore or migrate the other and assert ciphertext, metadata, and namespaces never cross-decrypt or cross-load
