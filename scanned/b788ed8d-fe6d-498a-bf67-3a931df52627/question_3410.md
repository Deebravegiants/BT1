# Q3410: jwt_session_id — unauthenticated bytes become the key via empty token

## Question
Starting from `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, can an unprivileged attacker supply an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback so that the cookie value is returned as the session id with no MAC, no signature and no shop binding? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `SessionUtils.jwt_session_id`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
