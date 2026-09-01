# Q1384: migrate_to_expiring_token — session keyed by claim via error-path body

## Question
Trace `TokenExchange.migrate_to_expiring_token` from `migrate_to_expiring_token(shop:, non_expiring_offline_token:)` with a 400 response whose `error` field steers the `invalid_subject_token` branch: because `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: a 400 response whose `error` field steers the `invalid_subject_token` branch
- Exploit idea: `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `exchange_token` sanitises `dest_shop` the same way `migrate_to_expiring_token` sanitises its `shop:` argument
