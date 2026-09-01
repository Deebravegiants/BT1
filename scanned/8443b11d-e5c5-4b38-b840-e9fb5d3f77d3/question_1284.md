# Q1284: migrate_to_expiring_token — no consumption tracking via attacker id token

## Question
If an unprivileged attacker submits a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install to `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, does `TokenExchange.migrate_to_expiring_token` end up acting on a value that was never authenticated, because a subject token can be exchanged repeatedly within its validity window? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install
- Exploit idea: a subject token can be exchanged repeatedly within its validity window
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
