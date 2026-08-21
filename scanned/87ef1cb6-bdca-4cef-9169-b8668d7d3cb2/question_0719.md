# Q0719: Token handling in Embedding (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker cause `Embedding` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) to fall back to a static/empty/previous authorization token when the fresh one is unavailable, so requests are made under an identity or authorization state that does not match the session?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `Embedding` (type)
- Entrypoint: Conditions that make the fresh token unavailable during their session
- Attacker controls: timing of the session relative to token refresh
- Exploit idea: Inspect the fallback branch of `Embedding` for a static or stale token.
- Invariant to test: An unavailable token is a hard failure, never a downgrade to a static or stale credential.
- Expected Immunefi impact: Requests authorized under an incorrect or stale credential
- Fast validation: Unit-test the fallback branch of `Embedding` asserting request refusal.
