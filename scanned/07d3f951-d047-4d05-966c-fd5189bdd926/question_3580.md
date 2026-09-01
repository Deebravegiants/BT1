# Q3580: expired? — temp restores unconditionally via shop with separator

## Question
If an unprivileged attacker submits a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair to `expired?`, which returns false whenever `@expires` is nil, does `Auth::Session#expired?` end up acting on a value that was never authenticated, because the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: a `shop` containing `_` so `"#{shop}_#{user_id}"` collides with another shop/user pair
- Exploit idea: the `ensure` block restores whatever was captured, which under nesting or threading may not be the caller's session
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
