# Q1254: refresh_token_expired? — identity built by interpolation via caller-supplied id

## Question
Starting from `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, can an unprivileged attacker supply the `id:` keyword, which lets a session be constructed under any storage key so that session ids are string concatenations of values that may contain the delimiter? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Auth::Session#refresh_token_expired?`, and whether the result reaches Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: the `id:` keyword, which lets a session be constructed under any storage key
- Exploit idea: session ids are string concatenations of values that may contain the delimiter
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
