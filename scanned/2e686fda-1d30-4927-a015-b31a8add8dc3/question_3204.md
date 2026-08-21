# Q3204: Cached/stale configuration reused by load_or_default (config.rs)

## Question
Can an unprivileged attacker exploit `load_or_default` in [src/config.rs](src/config.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/config.rs](src/config.rs) -> `load_or_default` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `load_or_default` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `load_or_default` with expired cache asserting fail-closed behaviour.
