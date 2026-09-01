# Q112: migrate_to_expiring_token — validated argument ignored via requested token type

## Question
Can an unprivileged attacker reach `TokenExchange.migrate_to_expiring_token` through `migrate_to_expiring_token(shop:, non_expiring_offline_token:)` while supplying the `requested_token_type:` argument, selecting an online or offline token for the same subject token, so that the `shop:` argument the caller validated is discarded, so the value validated and the value used differ, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the `requested_token_type:` argument, selecting an online or offline token for the same subject token
- Exploit idea: the `shop:` argument the caller validated is discarded, so the value validated and the value used differ
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `exchange_token` sanitises `dest_shop` the same way `migrate_to_expiring_token` sanitises its `shop:` argument
