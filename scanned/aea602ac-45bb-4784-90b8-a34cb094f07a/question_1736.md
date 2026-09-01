# Q1736: migrate_to_expiring_token — validated argument ignored via attacker id token

## Question
Can an unprivileged attacker reach `TokenExchange.migrate_to_expiring_token` through `migrate_to_expiring_token(shop:, non_expiring_offline_token:)` while supplying a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install, so that the `shop:` argument the caller validated is discarded, so the value validated and the value used differ, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install
- Exploit idea: the `shop:` argument the caller validated is discarded, so the value validated and the value used differ
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
