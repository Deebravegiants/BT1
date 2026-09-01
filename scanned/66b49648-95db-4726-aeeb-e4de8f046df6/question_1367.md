# Q1367: jwt_session_id — interpolation collision via cookie plus token

## Question
Does `SessionUtils.jwt_session_id` collapse two distinct identities into one when an unprivileged attacker submits a request presenting both a cookie and an id token with conflicting shops at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation? Show that string concatenation with `_` makes distinct identities collide, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
