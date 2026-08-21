# Q2013: Cached/stale configuration reused by Location (backend/status.rs)

## Question
Can an unprivileged attacker exploit `Location` in [src/backend/status.rs](src/backend/status.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/status.rs](src/backend/status.rs) -> `Location` (type)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `Location` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `Location` with expired cache asserting fail-closed behaviour.
