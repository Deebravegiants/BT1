# Q665: cookie_session_id — unauthenticated bytes become the key via shop with underscore

## Question
Can an unprivileged attacker reach `SessionUtils.cookie_session_id` through `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key while supplying a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key, so that the cookie value is returned as the session id with no MAC, no signature and no shop binding, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
