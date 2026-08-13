# Q584: lifecycle lifecycle state bleed via applicationLifecyclePlugin

## Question
Can an unprivileged attacker use wallet create/import/unlock/restore flow reachable from normal app usage with attacker-controlled `port`, `port`, and transition timing so that `applicationLifecyclePlugin` in `features/application/src/plugins/lifecycle.ts` cause lifecycle hooks or event emission to run before security-critical state is committed or validated, violating the rule that imported or restored state must bind only to the intended active seed and wallet account, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/application/src/plugins/lifecycle.ts::applicationLifecyclePlugin
- Entrypoint: wallet create/import/unlock/restore flow reachable from normal app usage
- Attacker controls: an imported backup or mnemonic payload, the passphrase field, and call ordering across create/import/unlock
- Exploit idea: cause lifecycle hooks or event emission to run before security-critical state is committed or validated
- Invariant to test: imported or restored state must bind only to the intended active seed and wallet account
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: exercise PIN/biometric fallback races and verify the locked state remains enforced until the full auth path succeeds
