# Q1847: jwt_session_id — unauthenticated bytes become the key via guessed offline key

## Question
Is there a reachable state in which an unprivileged attacker, controlling a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, makes `SessionUtils.jwt_session_id` return a result the caller treats as authenticated, given that the cookie value is returned as the session id with no MAC, no signature and no shop binding? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
