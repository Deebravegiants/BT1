# Q2637: session_id_from_shopify_id_token — fallback weakens the strong path via guessed offline key

## Question
Trace `SessionUtils.session_id_from_shopify_id_token` from `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims with a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint: because an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
