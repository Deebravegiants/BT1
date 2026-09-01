# Q2913: jwt_session_id — caller decides identity shape via shop casing

## Question
Starting from `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, can an unprivileged attacker supply a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings so that the `online` boolean, not the token, selects which identity is loaded? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `SessionUtils.jwt_session_id`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
