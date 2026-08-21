# Q2004: Cached/stale configuration reused by OrbOsVersionStatus (backend/orb_os_status.rs)

## Question
Can an unprivileged attacker exploit `OrbOsVersionStatus` in [src/backend/orb_os_status.rs](src/backend/orb_os_status.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/orb_os_status.rs](src/backend/orb_os_status.rs) -> `OrbOsVersionStatus` (type)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `OrbOsVersionStatus` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `OrbOsVersionStatus` with expired cache asserting fail-closed behaviour.
