# Q1888: Nonce/randomness reuse in IrisCodeSharesJson (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker induce nonce, salt, or blinding-factor reuse in `IrisCodeSharesJson` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) (restart, retry, non-CSPRNG source), weakening the encryption or commitment protecting biometric material?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `IrisCodeSharesJson` (type)
- Entrypoint: Repeated/retried signup attempts
- Attacker controls: timing and repetition that drives the retry path
- Exploit idea: Check the randomness source and per-use freshness of the nonce in `IrisCodeSharesJson`.
- Invariant to test: Every nonce/salt is freshly drawn from a CSPRNG and never reused across packages.
- Expected Immunefi impact: Biometric ciphertext or commitment weakened to recoverable
- Fast validation: Statistical test collecting nonces from repeated runs of `IrisCodeSharesJson` asserting uniqueness.
