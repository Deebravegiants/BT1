# Q2086: Nonce/randomness reuse in extension_report (debug_report.rs)

## Question
Can an unprivileged attacker induce nonce, salt, or blinding-factor reuse in `extension_report` in [src/debug_report.rs](src/debug_report.rs) (restart, retry, non-CSPRNG source), weakening the encryption or commitment protecting biometric material?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `extension_report` (function)
- Entrypoint: Repeated/retried signup attempts
- Attacker controls: timing and repetition that drives the retry path
- Exploit idea: Check the randomness source and per-use freshness of the nonce in `extension_report`.
- Invariant to test: Every nonce/salt is freshly drawn from a CSPRNG and never reused across packages.
- Expected Immunefi impact: Biometric ciphertext or commitment weakened to recoverable
- Fast validation: Statistical test collecting nonces from repeated runs of `extension_report` asserting uniqueness.
