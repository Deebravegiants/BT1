# Q3832: jwt_session_id — caller decides identity shape via omitted id token

## Question
If an unprivileged attacker submits an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch to `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation, does `SessionUtils.jwt_session_id` end up acting on a value that was never authenticated, because the `online` boolean, not the token, selects which identity is loaded? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
