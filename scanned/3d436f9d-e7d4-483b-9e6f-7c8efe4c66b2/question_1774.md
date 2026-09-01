# Q1774: expired? — nil means valid via shop with separator

## Question
If an unprivileged attacker submits a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair to `expired?`, which returns false whenever `@expires` is nil, does `Auth::Session#expired?` end up acting on a value that was never authenticated, because `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
