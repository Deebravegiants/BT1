# Q3294: Token handling in OrbMetadata (debug_report.rs)

## Question
Can an unprivileged attacker cause `OrbMetadata` in [src/debug_report.rs](src/debug_report.rs) to fall back to a static/empty/previous authorization token when the fresh one is unavailable, so requests are made under an identity or authorization state that does not match the session?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `OrbMetadata` (type)
- Entrypoint: Conditions that make the fresh token unavailable during their session
- Attacker controls: timing of the session relative to token refresh
- Exploit idea: Inspect the fallback branch of `OrbMetadata` for a static or stale token.
- Invariant to test: An unavailable token is a hard failure, never a downgrade to a static or stale credential.
- Expected Immunefi impact: Requests authorized under an incorrect or stale credential
- Fast validation: Unit-test the fallback branch of `OrbMetadata` asserting request refusal.
