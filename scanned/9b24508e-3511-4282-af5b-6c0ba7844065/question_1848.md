# Q1848: exchange_token — session keyed by claim via attacker id token

## Question
Can an unprivileged attacker reach `TokenExchange.exchange_token` through `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token while supplying a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install, so that `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - theft of a merchant's refresh token, granting durable access after rotation?

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install
- Exploit idea: `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
