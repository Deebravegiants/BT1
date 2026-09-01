# Q4392: session_id_from_shopify_id_token — no shop cross-check via cookie plus token

## Question
If an unprivileged attacker submits a request presenting both a cookie and an id token with conflicting shops to `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, does `SessionUtils.session_id_from_shopify_id_token` end up acting on a value that was never authenticated, because nothing asserts the loaded session's `shop` matches the shop authenticated by this request? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
