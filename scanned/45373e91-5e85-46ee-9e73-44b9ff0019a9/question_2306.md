# Q2306: session_id_from_shopify_id_token — no shop cross-check via omitted id token

## Question
If an unprivileged attacker submits an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch to `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, does `SessionUtils.session_id_from_shopify_id_token` end up acting on a value that was never authenticated, because nothing asserts the loaded session's `shop` matches the shop authenticated by this request? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an embedded request that simply omits the `Authorization` header, taking the cookie fallback branch
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
