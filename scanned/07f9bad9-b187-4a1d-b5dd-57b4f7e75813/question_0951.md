# Q951: refresh_token_expired? — id and shop can disagree via concurrent temp

## Question
Is there a reachable state in which an unprivileged attacker, controlling overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session at `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, makes `Auth::Session#refresh_token_expired?` return a result the caller treats as authenticated, given that `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: overlapping `Session.temp` blocks on threads sharing a `Concurrent::ThreadLocalVar` active session
- Exploit idea: `id` is caller-controlled and never re-derived from `shop`, so the storage key and the shop it holds a token for can differ
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: construct sessions for shops containing `_` and assert `Session.from` ids are injective across (shop, user) pairs
