# Q2807: start into_tee_authority equivalent-looking identities bypass equality

## Question
Can an unprivileged NEAR account enter through `sign` and use payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests to drive the code path through `crates/node/src/config/start.rs::into_tee_authority` so that equivalent-looking identities bypass equality or allowlist checks, breaking the invariant that identity-bearing strings and byte wrappers must be normalized once, before any security comparison, and leading to Unauthorized transaction?

## Target
- File/function: crates/node/src/config/start.rs:19::into_tee_authority
- Entrypoint: `sign`
- Attacker controls: payload bytes, derivation path, domain_id, attached deposit, predecessor identity, repeated submission timing, and overlapping requests
- Exploit idea: equivalent-looking identities bypass equality or allowlist checks
- Invariant to test: identity-bearing strings and byte wrappers must be normalized once, before any security comparison
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: exercise casing, prefix, leading-zero, and compressed/uncompressed variants and compare equality, hashing, and allowlist outcomes
