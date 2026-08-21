# Q1988: Cached/stale configuration reused by empty_string_is_none (backend/signup_poll.rs)

## Question
Can an unprivileged attacker exploit `empty_string_is_none` in [src/backend/signup_poll.rs](src/backend/signup_poll.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/signup_poll.rs](src/backend/signup_poll.rs) -> `empty_string_is_none` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `empty_string_is_none` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `empty_string_is_none` with expired cache asserting fail-closed behaviour.
