# Q1977: Cached/stale configuration reused by NETWORK_MONITOR_HOST (backend/endpoints.rs)

## Question
Can an unprivileged attacker exploit `NETWORK_MONITOR_HOST` in [src/backend/endpoints.rs](src/backend/endpoints.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/endpoints.rs](src/backend/endpoints.rs) -> `NETWORK_MONITOR_HOST` (item)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `NETWORK_MONITOR_HOST` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `NETWORK_MONITOR_HOST` with expired cache asserting fail-closed behaviour.
