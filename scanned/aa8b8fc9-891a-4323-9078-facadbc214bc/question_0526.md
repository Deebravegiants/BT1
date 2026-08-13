# Q526: passphrase cache restore-time auth gap via #scheduleClear

## Question
Can an unprivileged attacker use wallet unlock, relock, and reuse flow during normal app lifecycle with attacker-controlled `port`, `passphrase`, and transition timing so that `#scheduleClear` in `features/application/src/modules/passphrase-cache.ts` make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it, violating the rule that fallback authentication must not weaken the lock or approval policy enforced by the normal path, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/application/src/modules/passphrase-cache.ts::#scheduleClear
- Entrypoint: wallet unlock, relock, and reuse flow during normal app lifecycle
- Attacker controls: wallet-account selection, lifecycle hooks, and repeated start/load cycles
- Exploit idea: make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it
- Invariant to test: fallback authentication must not weaken the lock or approval policy enforced by the normal path
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: unit-test hook ordering and ensure no event fires with unlocked or imported state before validation and persistence complete
