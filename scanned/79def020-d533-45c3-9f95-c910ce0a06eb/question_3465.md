# Q3465: cookie_session_id — caller decides identity shape via shop casing

## Question
Can an unprivileged attacker reach `SessionUtils.cookie_session_id` through `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key while supplying a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings, so that the `online` boolean, not the token, selects which identity is loaded, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
