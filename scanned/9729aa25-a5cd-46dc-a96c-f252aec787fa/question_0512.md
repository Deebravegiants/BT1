# Q512: migrate_to_expiring_token — no consumption tracking via replayed subject token

## Question
Starting from `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, can an unprivileged attacker supply the same `subject_token` submitted repeatedly, since nothing tracks consumption so that a subject token can be exchanged repeatedly within its validity window? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `TokenExchange.migrate_to_expiring_token`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the same `subject_token` submitted repeatedly, since nothing tracks consumption
- Exploit idea: a subject token can be exchanged repeatedly within its validity window
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
