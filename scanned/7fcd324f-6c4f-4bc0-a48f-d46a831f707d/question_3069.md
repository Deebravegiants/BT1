# Q3069: jwt_session_id — interpolation collision via guessed online key

## Question
If an unprivileged attacker submits a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint to `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, does `SessionUtils.jwt_session_id` end up acting on a value that was never authenticated, because string concatenation with `_` makes distinct identities collide? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
