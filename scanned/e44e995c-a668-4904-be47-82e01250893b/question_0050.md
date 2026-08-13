# Q50: index fallback-auth weakness via createExodus

## Question
Can an unprivileged attacker use wallet create/import/unlock/restore flow reachable from normal app usage with attacker-controlled `xpub`, `config`, and transition timing so that `createExodus` in `sdks/headless/src/index.js` create a stale cross-wallet binding between account metadata and the active seed after import or clear, violating the rule that repeated lifecycle calls must be idempotent with respect to seed custody and account scoping, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: sdks/headless/src/index.js::createExodus
- Entrypoint: wallet create/import/unlock/restore flow reachable from normal app usage
- Attacker controls: a PIN/biometric fallback path and the order of user-visible approval steps
- Exploit idea: create a stale cross-wallet binding between account metadata and the active seed after import or clear
- Invariant to test: repeated lifecycle calls must be idempotent with respect to seed custody and account scoping
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: restore crafted state across multiple wallet accounts and assert only the intended seed/account pair is mutated or exposed
