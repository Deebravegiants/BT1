# Q2015: session_id_from_shopify_id_token — no shop cross-check via Bearer interior match

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, makes `SessionUtils.session_id_from_shopify_id_token` return a result the caller treats as authenticated, given that nothing asserts the loaded session's `shop` matches the shop authenticated by this request? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
