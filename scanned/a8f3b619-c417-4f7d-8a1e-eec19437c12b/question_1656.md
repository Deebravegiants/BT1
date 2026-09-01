# Q1656: exchange_token — shop taken from an unvalidated claim via dest-controlled host

## Question
Can the `dest` claim, which becomes `dest_shop` and then `Session.new(shop: dest_shop)` and then the request host, with no `ShopValidator` call, supplied by an unprivileged attacker at `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token, make `TokenExchange.exchange_token` and the code consuming its result disagree, given that `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: the `dest` claim, which becomes `dest_shop` and then `Session.new(shop: dest_shop)` and then the request host, with no `ShopValidator` call
- Exploit idea: `dest_shop` comes from `JwtPayload#shop` and is never passed through `ShopValidator.sanitize!`, unlike the sibling `migrate_to_expiring_token`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
