# Q107: index stale seed reuse via createApi

## Question
Can an unprivileged attacker use wallet create/import/unlock/restore flow reachable from normal app usage with attacker-controlled `name`, `method`, and transition timing so that `createApi` in `sdks/headless/src/api/index.js` make import, restore, or add-seed mutate the wrong wallet account or leave attacker-chosen state behind, violating the rule that lifecycle hooks and emitted events must reflect committed security state, not transient pre-validation state, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: sdks/headless/src/api/index.js::createApi
- Entrypoint: wallet create/import/unlock/restore flow reachable from normal app usage
- Attacker controls: a crafted state payload that is accepted during normal startup or restore
- Exploit idea: make import, restore, or add-seed mutate the wrong wallet account or leave attacker-chosen state behind
- Invariant to test: lifecycle hooks and emitted events must reflect committed security state, not transient pre-validation state
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: restore crafted state across multiple wallet accounts and assert only the intended seed/account pair is mutated or exposed
