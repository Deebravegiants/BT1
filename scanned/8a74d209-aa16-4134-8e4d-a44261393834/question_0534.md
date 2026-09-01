# Q534: migrate_to_expiring_token — shop taken from an unvalidated claim via requested token type

## Question
Does `TokenExchange.migrate_to_expiring_token` collapse two distinct identities into one when an unprivileged attacker submits the `requested_token_type:` argument, selecting an online or offline token for the same subject token at `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`? Show that `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: the `requested_token_type:` argument, selecting an online or offline token for the same subject token
- Exploit idea: `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
