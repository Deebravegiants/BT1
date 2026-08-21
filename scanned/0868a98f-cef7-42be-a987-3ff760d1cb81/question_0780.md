# Q0780: Nonce/randomness reuse in to_uuid (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker induce nonce, salt, or blinding-factor reuse in `to_uuid` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) (restart, retry, non-CSPRNG source), weakening the encryption or commitment protecting biometric material?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `to_uuid` (function)
- Entrypoint: Repeated/retried signup attempts
- Attacker controls: timing and repetition that drives the retry path
- Exploit idea: Check the randomness source and per-use freshness of the nonce in `to_uuid`.
- Invariant to test: Every nonce/salt is freshly drawn from a CSPRNG and never reused across packages.
- Expected Immunefi impact: Biometric ciphertext or commitment weakened to recoverable
- Fast validation: Statistical test collecting nonces from repeated runs of `to_uuid` asserting uniqueness.
