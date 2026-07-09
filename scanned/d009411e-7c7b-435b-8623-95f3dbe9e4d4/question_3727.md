# Q3727: commitment add equivalent-looking identities bypass equality

## Question
Can an unprivileged NEAR account enter through `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)` and use proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method to drive the code path through `crates/threshold-signatures/src/crypto/polynomials/commitment.rs::add` so that equivalent-looking identities bypass equality or allowlist checks, breaking the invariant that identity-bearing strings and byte wrappers must be normalized once, before any security comparison, and leading to Unauthorized transaction?

## Target
- File/function: crates/threshold-signatures/src/crypto/polynomials/commitment.rs:53::add
- Entrypoint: `public governance call path (propose_update / vote_update / vote_new_parameters / vote_add_domains / start_keygen_instance / start_reshare_instance)`
- Attacker controls: proposal contents, vote/removal timing, participant-churn timing, repeated calls, and any public arguments accepted by the method
- Exploit idea: equivalent-looking identities bypass equality or allowlist checks
- Invariant to test: identity-bearing strings and byte wrappers must be normalized once, before any security comparison
- Expected Immunefi impact: Unauthorized transaction
- Fast validation: exercise casing, prefix, leading-zero, and compressed/uncompressed variants and compare equality, hashing, and allowlist outcomes
