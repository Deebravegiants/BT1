# Q4283: refresh_token_expired? — nil means valid via online/offline flip

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?` at `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil, makes `Auth::Session#refresh_token_expired?` return a result the caller treats as authenticated, given that `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/session.rb` -> `Auth::Session#refresh_token_expired?`
- Entrypoint: `refresh_token_expired?`, which returns false whenever `@refresh_token_expires` is nil
- Attacker controls: an `is_online` value inconsistent with `associated_user`, since `@is_online` defaults to `!associated_user.nil?`
- Exploit idea: `expired?` and `refresh_token_expired?` treat missing expiry as never-expiring
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `copy_attributes_from` refuses to change `shop` on a session whose `id` encodes a different shop
