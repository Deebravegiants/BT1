# Q439: cookie_session_id — no shop cross-check via guessed online key

## Question
Trace `SessionUtils.cookie_session_id` from `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key with a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint: because nothing asserts the loaded session's `shop` matches the shop authenticated by this request, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
