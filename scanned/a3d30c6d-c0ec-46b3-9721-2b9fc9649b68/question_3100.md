# Q3100: Token handling in handle_save_thermal_data (agents/image_notary.rs)

## Question
Can an unprivileged attacker cause `handle_save_thermal_data` in [src/agents/image_notary.rs](src/agents/image_notary.rs) to fall back to a static/empty/previous authorization token when the fresh one is unavailable, so requests are made under an identity or authorization state that does not match the session?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `handle_save_thermal_data` (function)
- Entrypoint: Conditions that make the fresh token unavailable during their session
- Attacker controls: timing of the session relative to token refresh
- Exploit idea: Inspect the fallback branch of `handle_save_thermal_data` for a static or stale token.
- Invariant to test: An unavailable token is a hard failure, never a downgrade to a static or stale credential.
- Expected Immunefi impact: Requests authorized under an incorrect or stale credential
- Fast validation: Unit-test the fallback branch of `handle_save_thermal_data` asserting request refusal.
