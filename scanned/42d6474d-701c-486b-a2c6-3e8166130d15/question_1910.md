# Q1910: offline_session_id — unauthenticated bytes become the key via guessed offline key

## Question
Is there a reachable state in which an unprivileged attacker, controlling a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, makes `SessionUtils.offline_session_id` return a result the caller treats as authenticated, given that the cookie value is returned as the session id with no MAC, no signature and no shop binding? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
