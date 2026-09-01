# Q292: migrate_to_expiring_token — shop taken from an unvalidated claim via deprecated shop argument

## Question
Trace `TokenExchange.migrate_to_expiring_token` from `migrate_to_expiring_token(shop:, non_expiring_offline_token:)` with the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated: because `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated
- Exploit idea: `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `exchange_token` sanitises `dest_shop` the same way `migrate_to_expiring_token` sanitises its `shop:` argument
