# Q4243: expired? — nil means valid via associated_user id

## Question
Starting from `expired?`, which returns false whenever `@expires` is nil, can an unprivileged attacker supply the `associated_user.id` from the token response, interpolated into the session id so that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Auth::Session#expired?`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#expired?`
- Entrypoint: `expired?`, which returns false whenever `@expires` is nil
- Attacker controls: the `associated_user.id` from the token response, interpolated into the session id
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `expired?` is true, not false, for a session with no expiry once its token is past any plausible lifetime
