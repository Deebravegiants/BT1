# Q3153: Cached/stale configuration reused by format_eye_pipeline (backend/signup_post.rs)

## Question
Can an unprivileged attacker exploit `format_eye_pipeline` in [src/backend/signup_post.rs](src/backend/signup_post.rs) continuing to apply a cached configuration after refresh fails, so a stale permissive state persists indefinitely across their repeated signups?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `format_eye_pipeline` (function)
- Entrypoint: Repeated signups while refresh is failing
- Attacker controls: timing of their attempts relative to refresh failure
- Exploit idea: Check `format_eye_pipeline` for a max-age/hard-fail policy on stale configuration.
- Invariant to test: Configuration has a maximum age after which the flow fails closed.
- Expected Immunefi impact: Indefinitely stale security configuration governing signups
- Fast validation: Unit-test `format_eye_pipeline` with expired cache asserting fail-closed behaviour.
