# Q4088: jwt_session_id — no shop cross-check via non-embedded config

## Question
Can an unprivileged attacker reach `SessionUtils.jwt_session_id` through `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation while supplying an app configured `is_embedded: false`, where the cookie is the only accepted credential, so that nothing asserts the loaded session's `shop` matches the shop authenticated by this request, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: an app configured `is_embedded: false`, where the cookie is the only accepted credential
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
