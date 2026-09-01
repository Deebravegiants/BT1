# Q1925: session_id_from_shopify_id_token — fallback weakens the strong path via empty token

## Question
Can an unprivileged attacker reach `SessionUtils.session_id_from_shopify_id_token` through `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims while supplying an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback, so that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an empty or whitespace `shopify_id_token`, exercising the `MissingJwtTokenError` boundary versus the cookie fallback
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
