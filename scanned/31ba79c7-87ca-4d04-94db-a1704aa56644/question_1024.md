# Q1024: migrate_to_expiring_token — no consumption tracking via requested token type

## Question
Does `TokenExchange.migrate_to_expiring_token` collapse two distinct identities into one when an unprivileged attacker submits the `requested_token_type:` argument, selecting an online or offline token for the same subject token at `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`? Show that a subject token can be exchanged repeatedly within its validity window, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the `requested_token_type:` argument, selecting an online or offline token for the same subject token
- Exploit idea: a subject token can be exchanged repeatedly within its validity window
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `exchange_token` sanitises `dest_shop` the same way `migrate_to_expiring_token` sanitises its `shop:` argument
