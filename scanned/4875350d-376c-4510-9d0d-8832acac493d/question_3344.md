# Q3344: offline_session_id — interpolation collision via guessed online key

## Question
Trace `SessionUtils.offline_session_id` from `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation with a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint: because string concatenation with `_` makes distinct identities collide, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.offline_session_id`
- Entrypoint: `offline_session_id(shop)`, a bare `"offline_#{shop}"` interpolation
- Attacker controls: a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
