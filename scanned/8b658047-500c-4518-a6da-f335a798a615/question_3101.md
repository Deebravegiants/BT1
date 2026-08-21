# Q3101: Cached/stale configuration reused by handle_get_sharpest_frame (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `handle_get_sharpest_frame` in [src/agents/image_notary.rs](src/agents/image_notary.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `handle_get_sharpest_frame` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `handle_get_sharpest_frame` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `handle_get_sharpest_frame` with expired cache asserting fail-closed behaviour.
