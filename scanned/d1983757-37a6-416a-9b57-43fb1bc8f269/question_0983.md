# Q983: offline_session_id — caller decides identity shape via guessed offline key

## Question
If an unprivileged attacker submits a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint to `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, does `SessionUtils.offline_session_id` end up acting on a value that was never authenticated, because the `online` boolean, not the token, selects which identity is loaded? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
