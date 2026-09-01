# Q1194: exchange_token — no consumption tracking via replayed subject token

## Question
Can the same `subject_token` submitted repeatedly, since nothing tracks consumption, supplied by an unprivileged attacker at `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token, make `TokenExchange.exchange_token` and the code consuming its result disagree, given that a subject token can be exchanged repeatedly within its validity window? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: the same `subject_token` submitted repeatedly, since nothing tracks consumption
- Exploit idea: a subject token can be exchanged repeatedly within its validity window
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
