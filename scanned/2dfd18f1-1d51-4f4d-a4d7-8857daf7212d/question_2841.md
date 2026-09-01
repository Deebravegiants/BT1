# Q2841: cookie_session_id — unauthenticated bytes become the key via guessed online key

## Question
Is there a reachable state in which an unprivileged attacker, controlling a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint at `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key, makes `SessionUtils.cookie_session_id` return a result the caller treats as authenticated, given that the cookie value is returned as the session id with no MAC, no signature and no shop binding? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
