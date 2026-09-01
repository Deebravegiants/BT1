# Q1970: current_session_id — interpolation collision via non-embedded config

## Question
If an unprivileged attacker submits an app configured `is_embedded: false`, where the cookie is the only accepted credential to `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves, does `SessionUtils.current_session_id` end up acting on a value that was never authenticated, because string concatenation with `_` makes distinct identities collide? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/utils/session_utils.rb` -> `SessionUtils.current_session_id`
- Entrypoint: `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, cookies, online)`, called on every authenticated request the app serves
- Attacker controls: an app configured `is_embedded: false`, where the cookie is the only accepted credential
- Exploit idea: string concatenation with `_` makes distinct identities collide
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: fuzz shop/sub pairs containing `_` and assert `jwt_session_id` is injective
