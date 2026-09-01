# Q1301: session_id_from_shopify_id_token — caller decides identity shape via Bearer interior match

## Question
Is there a reachable state in which an unprivileged attacker, controlling an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, makes `SessionUtils.session_id_from_shopify_id_token` return a result the caller treats as authenticated, given that the `online` boolean, not the token, selects which identity is loaded? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an `Authorization` value where `gsub("Bearer ", "")` strips an interior occurrence and changes the token that gets decoded
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
