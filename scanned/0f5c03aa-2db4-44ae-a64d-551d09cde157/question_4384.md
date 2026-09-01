# Q4384: current_session_id — unauthenticated bytes become the key via omitted id token

## Question
Does `SessionUtils.current_session_id` collapse two distinct identities into one when an unprivileged attacker submits an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch at `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves? Show that the cookie value is returned as the session id with no MAC, no signature and no shop binding, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.current_session_id`
- Entrypoint: `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves
- Attacker controls: an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
