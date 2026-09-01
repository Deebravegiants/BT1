# Q2030: session_id_from_shopify_id_token — caller decides identity shape via non-embedded config

## Question
Can an unprivileged attacker reach `SessionUtils.session_id_from_shopify_id_token` through `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims while supplying an app configured `is_embedded: false`, where the cookie is the only accepted credential, so that the `online` boolean, not the token, selects which identity is loaded, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: an app configured `is_embedded: false`, where the cookie is the only accepted credential
- Exploit idea: the `online` boolean, not the token, selects which identity is loaded
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
