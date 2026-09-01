# Q4464: current_session_id — caller decides identity shape via omitted id token

## Question
Trace `SessionUtils.current_session_id` from `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves with an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch: because the `online` boolean, not the token, selects which identity is loaded, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.current_session_id`
- Entrypoint: `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves
- Attacker controls: an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
