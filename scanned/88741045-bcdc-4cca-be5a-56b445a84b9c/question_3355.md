# Q3355: session_id_from_shopify_id_token — unauthenticated bytes become the key via guessed online key

## Question
Does `SessionUtils.session_id_from_shopify_id_token` collapse two distinct identities into one when an unprivileged attacker submits a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims? Show that the cookie value is returned as the session id with no MAC, no signature and no shop binding, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: a cookie set to `<victim>.myshopify.com_<user id>`, matching what `jwt_session_id` would mint
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
