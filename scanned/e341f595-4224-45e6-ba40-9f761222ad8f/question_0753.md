# Q753: offline_session_id — key is predictable via shop casing

## Question
Can a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings, supplied by an unprivileged attacker at `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation, make `SessionUtils.offline_session_id` and the code consuming its result disagree, given that `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a shop value differing only in case or trailing dot from the stored key, since keys are compared as raw strings
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: call `current_session_id(nil, {'shopify_app_session' => 'offline_victim.myshopify.com'}, false)` and assert the returned key is not accepted as an identity
