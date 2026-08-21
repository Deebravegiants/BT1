# Q3039: Nonce/randomness reuse in salted_sha256 (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker induce nonce, salt, or blinding-factor reuse in `salted_sha256` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) (restart, retry, non-CSPRNG source), weakening the encryption or commitment protecting biometric material?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `salted_sha256` (function)
- Entrypoint: Repeated/retried signup attempts
- Attacker controls: timing and repetition that drives the retry path
- Exploit idea: Check the randomness source and per-use freshness of the nonce in `salted_sha256`.
- Invariant to test: Every nonce/salt is freshly drawn from a CSPRNG and never reused across packages.
- Expected Immunefi impact: Biometric ciphertext or commitment weakened to recoverable
- Fast validation: Statistical test collecting nonces from repeated runs of `salted_sha256` asserting uniqueness.
