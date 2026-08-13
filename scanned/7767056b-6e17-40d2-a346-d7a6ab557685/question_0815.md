# Q815: biometry.ios hook ordering bypass via createBiometry

## Question
Can an unprivileged attacker use mobile unlock or approval flow that invokes PIN/biometric authentication with attacker-controlled `method`, `port`, and transition timing so that `createBiometry` in `features/auth-mobile/module/bio/biometry.ios.js` bypass a lock or approval boundary during restart, auto-unlock, or fallback-auth flows, violating the rule that lock, clear, import, and restore must fully reset secrets, approvals, and account bindings before reuse, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/auth-mobile/module/bio/biometry.ios.js::createBiometry
- Entrypoint: mobile unlock or approval flow that invokes PIN/biometric authentication
- Attacker controls: repeat create, import, lock, unlock, restart, or restore actions with attacker-chosen timing
- Exploit idea: bypass a lock or approval boundary during restart, auto-unlock, or fallback-auth flows
- Invariant to test: lock, clear, import, and restore must fully reset secrets, approvals, and account bindings before reuse
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: exercise PIN/biometric fallback races and verify the locked state remains enforced until the full auth path succeeds
