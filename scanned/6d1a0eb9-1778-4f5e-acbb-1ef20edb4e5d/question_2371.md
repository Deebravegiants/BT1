# Q2371: jwt_session_id — no shop cross-check via guessed offline key

## Question
Trace `SessionUtils.jwt_session_id` from `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation with a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint: because nothing asserts the loaded session's `shop` matches the shop authenticated by this request, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
