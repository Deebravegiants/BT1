# Q0708: Cached/stale configuration reused by Plan (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit `Plan` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `Plan` (type)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `Plan` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `Plan` with expired cache asserting fail-closed behaviour.
