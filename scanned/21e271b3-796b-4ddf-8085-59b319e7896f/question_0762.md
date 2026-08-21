# Q0762: Cached/stale configuration reused by ssd_save_png (agents/image_notary.rs)

## Question
Can an unprivileged attacker exploit `ssd_save_png` in [src/agents/image_notary.rs](src/agents/image_notary.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `ssd_save_png` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `ssd_save_png` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `ssd_save_png` with expired cache asserting fail-closed behaviour.
