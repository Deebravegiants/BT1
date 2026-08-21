# Q1918: Nonce/randomness reuse in save_identification_images (agents/image_notary.rs)

## Question
Can an unprivileged attacker induce nonce, salt, or blinding-factor reuse in `save_identification_images` in [src/agents/image_notary.rs](src/agents/image_notary.rs) (restart, retry, non-CSPRNG source), weakening the encryption or commitment protecting biometric material?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `save_identification_images` (function)
- Entrypoint: Repeated/retried signup attempts
- Attacker controls: timing and repetition that drives the retry path
- Exploit idea: Check the randomness source and per-use freshness of the nonce in `save_identification_images`.
- Invariant to test: Every nonce/salt is freshly drawn from a CSPRNG and never reused across packages.
- Expected Immunefi impact: Biometric ciphertext or commitment weakened to recoverable
- Fast validation: Statistical test collecting nonces from repeated runs of `save_identification_images` asserting uniqueness.
