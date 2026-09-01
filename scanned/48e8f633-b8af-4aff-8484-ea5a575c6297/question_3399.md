# Q3399: cookie_session_id — key is predictable via empty token

## Question
Can an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback, supplied by an unprivileged attacker at `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key, make `SessionUtils.cookie_session_id` and the code consuming its result disagree, given that `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
