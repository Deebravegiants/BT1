# Q189: offline_session_id — unauthenticated bytes become the key via chosen cookie value

## Question
Can an unprivileged attacker reach `SessionUtils.offline_session_id` through `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation while supplying the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check, so that the cookie value is returned as the session id with no MAC, no signature and no shop binding, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - theft of a merchant's refresh token, granting durable access after rotation?

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
