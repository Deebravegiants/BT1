# Q0795: Cached/stale configuration reused by client_with_timeouts (backend/mod.rs)

## Question
Can an unprivileged attacker exploit `client_with_timeouts` in [src/backend/mod.rs](src/backend/mod.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/mod.rs](src/backend/mod.rs) -> `client_with_timeouts` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `client_with_timeouts` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `client_with_timeouts` with expired cache asserting fail-closed behaviour.
