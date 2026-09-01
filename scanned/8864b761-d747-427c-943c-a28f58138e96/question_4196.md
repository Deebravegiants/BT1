# Q4196: jwt_session_id — fallback weakens the strong path via guessed offline key

## Question
If an unprivileged attacker submits a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint to `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, does `SessionUtils.jwt_session_id` end up acting on a value that was never authenticated, because an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a cookie set to `offline_<victim>.myshopify.com`, matching exactly what `offline_session_id` would mint
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
