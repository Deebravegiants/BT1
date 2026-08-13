# Q781: biometry.android restore-time auth gap via createBiometry

## Question
Can an unprivileged attacker use mobile unlock or approval flow that invokes PIN/biometric authentication with attacker-controlled `port`, `message`, and transition timing so that `createBiometry` in `features/auth-mobile/module/bio/biometry.android.js` make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it, violating the rule that fallback authentication must not weaken the lock or approval policy enforced by the normal path, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/auth-mobile/module/bio/biometry.android.js::createBiometry
- Entrypoint: mobile unlock or approval flow that invokes PIN/biometric authentication
- Attacker controls: wallet-account selection, lifecycle hooks, and repeated start/load cycles
- Exploit idea: make old unlocked material, old seed state, or old account scope survive a lifecycle transition that should clear it
- Invariant to test: fallback authentication must not weaken the lock or approval policy enforced by the normal path
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: exercise PIN/biometric fallback races and verify the locked state remains enforced until the full auth path succeeds
