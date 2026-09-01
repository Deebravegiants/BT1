# Q1139: cookie_session_id — unauthenticated bytes become the key via shop casing

## Question
Trace `SessionUtils.cookie_session_id` from `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key with a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings: because the cookie value is returned as the session id with no MAC, no signature and no shop binding, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
