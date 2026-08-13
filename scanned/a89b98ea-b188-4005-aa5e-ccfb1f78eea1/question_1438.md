# Q1438: utils stale seed reuse via NamedError

## Question
Can an unprivileged attacker use wallet create/import/unlock/restore flow reachable from normal app usage with attacker-controlled `message`, `name`, and transition timing so that `NamedError` in `features/wallet/module/utils.js` make import, restore, or add-seed mutate the wrong wallet account or leave attacker-chosen state behind, violating the rule that lifecycle hooks and emitted events must reflect committed security state, not transient pre-validation state, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/wallet/module/utils.js::NamedError
- Entrypoint: wallet create/import/unlock/restore flow reachable from normal app usage
- Attacker controls: a crafted state payload that is accepted during normal startup or restore
- Exploit idea: make import, restore, or add-seed mutate the wrong wallet account or leave attacker-chosen state behind
- Invariant to test: lifecycle hooks and emitted events must reflect committed security state, not transient pre-validation state
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: exercise PIN/biometric fallback races and verify the locked state remains enforced until the full auth path succeeds
