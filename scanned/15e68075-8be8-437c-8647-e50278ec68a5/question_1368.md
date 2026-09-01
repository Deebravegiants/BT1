# Q1368: migrate_to_expiring_token — shop taken from an unvalidated claim via expiring flag

## Question
If an unprivileged attacker submits `Context.expiring_offline_access_tokens`, which changes the body sent and the session's expiry to `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, does `TokenExchange.migrate_to_expiring_token` end up acting on a value that was never authenticated, because `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: `Context.expiring_offline_access_tokens`, which changes the body sent and the session's expiry
- Exploit idea: `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
