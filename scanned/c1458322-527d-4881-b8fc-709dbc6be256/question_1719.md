# Q1719: cookie_session_id — caller decides identity shape via Bearer interior match

## Question
Can an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded, supplied by an unprivileged attacker at `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key, make `SessionUtils.cookie_session_id` and the code consuming its result disagree, given that the `online` boolean, not the token, selects which identity is loaded? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
