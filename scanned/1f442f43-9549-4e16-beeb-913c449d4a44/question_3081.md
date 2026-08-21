# Q3081: Nonce/randomness reuse in request_orb_token (short_lived_token.rs)

## Question
Can an unprivileged attacker induce nonce, salt, or blinding-factor reuse in `request_orb_token` in [src/short_lived_token.rs](src/short_lived_token.rs) (restart, retry, non-CSPRNG source), weakening the encryption or commitment protecting biometric material?

## Target
- File/function: [src/short_lived_token.rs](src/short_lived_token.rs) -> `request_orb_token` (function)
- Entrypoint: Repeated/retried signup attempts
- Attacker controls: timing and repetition that drives the retry path
- Exploit idea: Check the randomness source and per-use freshness of the nonce in `request_orb_token`.
- Invariant to test: Every nonce/salt is freshly drawn from a CSPRNG and never reused across packages.
- Expected Immunefi impact: Biometric ciphertext or commitment weakened to recoverable
- Fast validation: Statistical test collecting nonces from repeated runs of `request_orb_token` asserting uniqueness.
