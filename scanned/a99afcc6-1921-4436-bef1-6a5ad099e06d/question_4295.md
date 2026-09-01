# Q4295: shopify_user_id — type assumptions via dest with embedded separator

## Question
Can a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator, supplied by an unprivileged attacker at `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`, make `JwtPayload#shopify_user_id` and the code consuming its result disagree, given that `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shopify_user_id`
- Entrypoint: `shopify_user_id`, gated by `user_id_sub?` and `admin_session_token?`
- Attacker controls: a `dest` whose host contains `_` or `/`, which later collides with the `#{shop}_#{sub}` session-id separator
- Exploit idea: `T.let` casts assume claim types; a differently-typed claim reaches downstream string interpolation
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: craft `sub` values containing `_` and assert `SessionUtils.jwt_session_id` cannot be made to collide across users
