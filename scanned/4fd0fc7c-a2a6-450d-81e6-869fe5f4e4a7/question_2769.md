# Q2769: session_id_from_shopify_id_token — caller decides identity shape via cookie plus token

## Question
Can a request presenting both a cookie and an id token with conflicting shops, supplied by an unprivileged attacker at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, make `SessionUtils.session_id_from_shopify_id_token` and the code consuming its result disagree, given that the `online` boolean, not the token, selects which identity is loaded? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: a request presenting both a cookie and an id token with conflicting shops
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
