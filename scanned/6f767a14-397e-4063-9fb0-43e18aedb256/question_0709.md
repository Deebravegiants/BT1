# Q709: jwt_session_id — no shop cross-check via shop with underscore

## Question
Does `SessionUtils.jwt_session_id` collapse two distinct identities into one when an unprivileged attacker submits a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key at `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation? Show that nothing asserts the loaded session's `shop` matches the shop authenticated by this request, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.jwt_session_id`
- Entrypoint: `jwt_session_id(shop, user_id)`, a bare `"#{shop}_#{user_id}"` interpolation
- Attacker controls: a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert an embedded app rejects a request with no `Authorization` header rather than falling back to the cookie
