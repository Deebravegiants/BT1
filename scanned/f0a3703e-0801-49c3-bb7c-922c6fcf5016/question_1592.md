# Q1592: migrate_to_expiring_token — validated argument ignored via dest-controlled host

## Question
If an unprivileged attacker submits the `dest` claim, which becomes `dest_shop` and then `Session.new(shop: dest_shop)` and then the request host, with no `ShopValidator` call to `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, does `TokenExchange.migrate_to_expiring_token` end up acting on a value that was never authenticated, because the `shop:` argument the caller validated is discarded, so the value validated and the value used differ? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the `dest` claim, which becomes `dest_shop` and then `Session.new(shop: dest_shop)` and then the request host, with no `ShopValidator` call
- Exploit idea: the `shop:` argument the caller validated is discarded, so the value validated and the value used differ
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
