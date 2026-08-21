# Q0868: Cached/stale configuration reused by language (config.rs)

## Question
Can an unprivileged attacker exploit `language` in [src/config.rs](src/config.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/config.rs](src/config.rs) -> `language` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `language` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `language` with expired cache asserting fail-closed behaviour.
