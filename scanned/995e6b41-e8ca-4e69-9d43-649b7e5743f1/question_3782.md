# Q3782: offline_session_id — unauthenticated bytes become the key via cookie plus token

## Question
Does `SessionUtils.offline_session_id` collapse two distinct identities into one when an unprivileged attacker submits a request presenting both a cookie and an id token with conflicting shops at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation? Show that the cookie value is returned as the session id with no MAC, no signature and no shop binding, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
