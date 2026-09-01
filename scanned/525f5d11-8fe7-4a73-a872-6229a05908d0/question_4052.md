# Q4052: offline_session_id — unauthenticated bytes become the key via Bearer interior match

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, makes `SessionUtils.offline_session_id` return a result the caller treats as authenticated, given that the cookie value is returned as the session id with no MAC, no signature and no shop binding? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
