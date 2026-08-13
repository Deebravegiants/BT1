# Q610: lifecycle hook ordering bypass via onLoad

## Question
Can an unprivileged attacker use wallet create/import/unlock/restore flow reachable from normal app usage with attacker-controlled `port`, `port`, and transition timing so that `onLoad` in `features/application/src/plugins/lifecycle.ts` bypass a lock or approval boundary during restart, auto-unlock, or fallback-auth flows, violating the rule that lock, clear, import, and restore must fully reset secrets, approvals, and account bindings before reuse, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/application/src/plugins/lifecycle.ts::onLoad
- Entrypoint: wallet create/import/unlock/restore flow reachable from normal app usage
- Attacker controls: repeat create, import, lock, unlock, restart, or restore actions with attacker-chosen timing
- Exploit idea: bypass a lock or approval boundary during restart, auto-unlock, or fallback-auth flows
- Invariant to test: lock, clear, import, and restore must fully reset secrets, approvals, and account bindings before reuse
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: unit-test hook ordering and ensure no event fires with unlocked or imported state before validation and persistence complete
