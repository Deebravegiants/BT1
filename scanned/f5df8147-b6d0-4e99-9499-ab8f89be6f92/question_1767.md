# Q1767: session_id_from_shopify_id_token — no shop cross-check via shop casing

## Question
If an unprivileged attacker submits a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings to `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, does `SessionUtils.session_id_from_shopify_id_token` end up acting on a value that was never authenticated, because nothing asserts the loaded session's `shop` matches the shop authenticated by this request? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
