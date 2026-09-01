# Q1302: exchange_token — shop taken from an unvalidated claim via deprecated shop argument

## Question
Can an unprivileged attacker reach `TokenExchange.exchange_token` through `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token while supplying the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated, so that `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: the still-accepted `shop:` keyword, which is now ignored in favour of `dest` but may be what the host app validated
- Exploit idea: `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
