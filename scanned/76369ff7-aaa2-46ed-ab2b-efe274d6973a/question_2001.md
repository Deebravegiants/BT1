# Q2001: wallet accounts restore-time auth gap via clear

## Question
Can an unprivileged attacker use wallet create/import/unlock/restore flow reachable from normal app usage with attacker-controlled `config`, `name`, and transition timing so that `clear` in `features/wallet-accounts/src/module/wallet-accounts.ts` make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it, violating the rule that fallback authentication must not weaken the lock or approval policy enforced by the normal path, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/wallet-accounts/src/module/wallet-accounts.ts::clear
- Entrypoint: wallet create/import/unlock/restore flow reachable from normal app usage
- Attacker controls: wallet-account selection, lifecycle hooks, and repeated start/load cycles
- Exploit idea: make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it
- Invariant to test: fallback authentication must not weaken the lock or approval policy enforced by the normal path
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: exercise PIN/biometric fallback races and verify the locked state remains enforced until the full auth path succeeds
