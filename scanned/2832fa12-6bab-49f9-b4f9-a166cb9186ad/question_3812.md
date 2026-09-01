# Q3812: cookie_session_id — fallback weakens the strong path via guessed online key

## Question
Can a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint, supplied by an unprivileged attacker at `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key, make `SessionUtils.cookie_session_id` and the code consuming its result disagree, given that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.cookie_session_id`
- Entrypoint: `cookie_session_id`, which returns `cookies['shopify_app_session']` verbatim as the storage key
- Attacker controls: a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
