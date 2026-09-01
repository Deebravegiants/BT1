# Q1229: session_id_from_shopify_id_token — key is predictable via non-embedded config

## Question
Can an app configured `is_embedded: false`, where the cookie is the only accepted credential, supplied by an unprivileged attacker at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, make `SessionUtils.session_id_from_shopify_id_token` and the code consuming its result disagree, given that `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an app configured `is_embedded: false`, where the cookie is the only accepted credential
- Exploit idea: `offline_#{shop}` and `#{shop}_#{user_id}` are fully derivable from public information
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
