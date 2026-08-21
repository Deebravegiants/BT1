# Q1995: Cached/stale configuration reused by Response (backend/user_status.rs)

## Question
Can an unprivileged attacker exploit `Response` in [src/backend/user_status.rs](src/backend/user_status.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/user_status.rs](src/backend/user_status.rs) -> `Response` (type)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `Response` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `Response` with expired cache asserting fail-closed behaviour.
