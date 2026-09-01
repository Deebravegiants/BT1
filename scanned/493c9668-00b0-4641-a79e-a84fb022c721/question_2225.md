# Q2225: session_id_from_shopify_id_token — fallback weakens the strong path via chosen cookie value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, makes `SessionUtils.session_id_from_shopify_id_token` return a result the caller treats as authenticated, given that an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: the `shopify_app_session` cookie, whose value the gem returns as the session key without any signature check
- Exploit idea: an embedded app that would otherwise require a signed id token accepts a cookie whenever the header is absent
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
