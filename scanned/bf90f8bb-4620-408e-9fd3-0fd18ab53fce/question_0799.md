# Q0799: Cached/stale configuration reused by Config (backend/config.rs)

## Question
Can an unprivileged attacker exploit `Config` in [src/backend/config.rs](src/backend/config.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/config.rs](src/backend/config.rs) -> `Config` (type)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `Config` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `Config` with expired cache asserting fail-closed behaviour.
