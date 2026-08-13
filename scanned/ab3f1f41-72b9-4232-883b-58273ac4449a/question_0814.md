# Q814: biometry.ios lifecycle state bleed via Biometry

## Question
Can an unprivileged attacker use mobile unlock or approval flow that invokes PIN/biometric authentication with attacker-controlled `port`, `method`, and transition timing so that `Biometry` in `features/auth-mobile/module/bio/biometry.ios.js` cause lifecycle hooks or event emission to run before security-critical state is committed or validated, violating the rule that imported or restored state must bind only to the intended active seed and wallet account, and ultimately reaching `Private key or private key generation leakage leading to unauthorized access to user funds`?

## Target
- File/function: features/auth-mobile/module/bio/biometry.ios.js::Biometry
- Entrypoint: mobile unlock or approval flow that invokes PIN/biometric authentication
- Attacker controls: an imported backup or mnemonic payload, the passphrase field, and call ordering across create/import/unlock
- Exploit idea: cause lifecycle hooks or event emission to run before security-critical state is committed or validated
- Invariant to test: imported or restored state must bind only to the intended active seed and wallet account
- Expected Immunefi impact: Private key or private key generation leakage leading to unauthorized access to user funds
- Fast validation: script create/import/lock/unlock/restart sequences and assert old secrets, accounts, and approvals cannot be reused after the reset point
