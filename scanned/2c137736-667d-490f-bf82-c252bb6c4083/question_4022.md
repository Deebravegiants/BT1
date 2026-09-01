# Q4022: session_id_from_shopify_id_token — no shop cross-check via shop with underscore

## Question
Can a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key, supplied by an unprivileged attacker at `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims, make `SessionUtils.session_id_from_shopify_id_token` and the code consuming its result disagree, given that nothing asserts the loaded session's `shop` matches the shop authenticated by this request? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.session_id_from_shopify_id_token`
- Entrypoint: `session_id_from_shopify_id_token(id_token:, online:)`, which builds the storage key from JWT claims
- Attacker controls: a shop or `sub` value containing `_` so two distinct (shop, user) pairs map to one key
- Exploit idea: nothing asserts the loaded session's `shop` matches the shop authenticated by this request
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
