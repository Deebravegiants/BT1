# Q1879: session_id_from_shopify_id_token — interpolation collision via omitted id token

## Question
If an unprivileged attacker submits an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch to `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, does `SessionUtils.session_id_from_shopify_id_token` end up acting on a value that was never authenticated, because string concatenation with `_` makes distinct identities collide? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
