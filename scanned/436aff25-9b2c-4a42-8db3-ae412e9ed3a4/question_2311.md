# Q2311: expired? — id and shop can disagree via concurrent temp

## Question
Starting from `expired?`, which returns false whenever `@expires` is nil, can an unprivileged attacker supply overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session so that `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Auth::Session#expired?`, and whether the result reaches Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
