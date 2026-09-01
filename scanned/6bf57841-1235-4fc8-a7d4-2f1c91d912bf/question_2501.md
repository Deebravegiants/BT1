# Q2501: session_id_from_shopify_id_token — unauthenticated bytes become the key via omitted id token

## Question
Does `SessionUtils.session_id_from_shopify_id_token` collapse two distinct identities into one when an unprivileged attacker submits an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims? Show that the cookie value is returned as the session id with no MAC, no signature and no shop binding, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch
- Exploit idea: the cookie value is returned as the session id with no MAC, no signature and no shop binding
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
