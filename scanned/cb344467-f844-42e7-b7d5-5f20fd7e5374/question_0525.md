# Q525: passphrase cache hook ordering bypass via #getTtl

## Question
Can an unprivileged attacker use wallet unlock, relock, and reuse flow during normal app lifecycle with attacker-controlled `config`, `port`, and transition timing so that `#getTtl` in `features/application/src/modules/passphrase-cache.ts` bypass a lock or approval boundary during restart, auto-unlock, or fallback-auth flows, violating the rule that lock, clear, import, and restore must fully reset secrets, approvals, and account bindings before reuse, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/application/src/modules/passphrase-cache.ts::#getTtl
- Entrypoint: wallet unlock, relock, and reuse flow during normal app lifecycle
- Attacker controls: repeat create, import, lock, unlock, restart, or restore actions with attacker-chosen timing
- Exploit idea: bypass a lock or approval boundary during restart, auto-unlock, or fallback-auth flows
- Invariant to test: lock, clear, import, and restore must fully reset secrets, approvals, and account bindings before reuse
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: restore crafted state across multiple wallet accounts and assert only the intended seed/account pair is mutated or exposed
