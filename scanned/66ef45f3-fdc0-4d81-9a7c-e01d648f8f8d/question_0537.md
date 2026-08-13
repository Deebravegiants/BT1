# Q537: passphrase cache stale seed reuse via #getTtl

## Question
Can an unprivileged attacker use wallet unlock, relock, and reuse flow during normal app lifecycle with attacker-controlled `config`, `port`, and transition timing so that `#getTtl` in `features/application/src/modules/passphrase-cache.ts` make import, restore, or add-seed mutate the wrong wallet account or leave attacker-chosen state behind, violating the rule that lifecycle hooks and emitted events must reflect committed security state, not transient pre-validation state, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/application/src/modules/passphrase-cache.ts::#getTtl
- Entrypoint: wallet unlock, relock, and reuse flow during normal app lifecycle
- Attacker controls: a crafted state payload that is accepted during normal startup or restore
- Exploit idea: make import, restore, or add-seed mutate the wrong wallet account or leave attacker-chosen state behind
- Invariant to test: lifecycle hooks and emitted events must reflect committed security state, not transient pre-validation state
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: restore crafted state across multiple wallet accounts and assert only the intended seed/account pair is mutated or exposed
