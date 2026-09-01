# Q1576: migrate_to_expiring_token — error branch reveals verdict via replayed subject token

## Question
Starting from `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, can an unprivileged attacker supply the same `subject_token` submitted repeatedly, since nothing tracks consumption so that distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `TokenExchange.migrate_to_expiring_token`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the same `subject_token` submitted repeatedly, since nothing tracks consumption
- Exploit idea: distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `exchange_token` sanitises `dest_shop` the same way `migrate_to_expiring_token` sanitises its `shop:` argument
