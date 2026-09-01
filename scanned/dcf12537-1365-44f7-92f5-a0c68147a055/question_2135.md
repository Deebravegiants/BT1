# Q2135: jwt_session_id — interpolation collision via shop with underscore

## Question
Can an unprivileged attacker reach `SessionUtils.jwt_session_id` through `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation while supplying a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key, so that string concatenation with `_` makes distinct identities collide, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
