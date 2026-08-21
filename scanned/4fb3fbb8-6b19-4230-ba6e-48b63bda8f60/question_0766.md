# Q0766: Cached/stale configuration reused by init_image_notary (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `init_image_notary` in [src/agents/image_notary.rs](src/agents/image_notary.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `init_image_notary` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `init_image_notary` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `init_image_notary` with expired cache asserting fail-closed behaviour.
