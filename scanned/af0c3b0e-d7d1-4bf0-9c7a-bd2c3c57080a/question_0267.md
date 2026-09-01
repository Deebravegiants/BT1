# Q267: exchange_token — session keyed by claim via non-embedded / private config

## Question
Starting from `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token, can an unprivileged attacker supply an app configuration that flips the `Context.private?` and `Context.embedded?` guards so that `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `TokenExchange.exchange_token`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: an app configuration that flips the `Context.private?` and `Context.embedded?` guards
- Exploit idea: `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
