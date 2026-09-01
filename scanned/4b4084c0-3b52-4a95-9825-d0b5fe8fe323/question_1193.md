# Q1193: cookie_session_id — interpolation collision via guessed online key

## Question
If an unprivileged attacker submits a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint to `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key, does `SessionUtils.cookie_session_id` end up acting on a value that was never authenticated, because string concatenation with `_` makes distinct identities collide? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
