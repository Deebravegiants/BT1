# Q581: passphrase cache restore-time auth gap via #getTtl

## Question
Can an unprivileged attacker use wallet unlock, relock, and reuse flow during normal app lifecycle with attacker-controlled `passphrase`, `config`, and transition timing so that `#getTtl` in `features/application/src/modules/passphrase-cache.ts` make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it, violating the rule that fallback authentication must not weaken the lock or approval policy enforced by the normal path, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/application/src/modules/passphrase-cache.ts::#getTtl
- Entrypoint: wallet unlock, relock, and reuse flow during normal app lifecycle
- Attacker controls: wallet-account selection, lifecycle hooks, and repeated start/load cycles
- Exploit idea: make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it
- Invariant to test: fallback authentication must not weaken the lock or approval policy enforced by the normal path
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: restore crafted state across multiple wallet accounts and assert only the intended seed/account pair is mutated or exposed
