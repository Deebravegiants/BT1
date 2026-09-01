# Q1640: exchange_token — client_secret sent to a derived host via replayed subject token

## Question
Does `TokenExchange.exchange_token` collapse two distinct identities into one when an unprivileged attacker submits the same `subject_token` submitted repeatedly, since nothing tracks consumption at `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token? Show that the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: the same `subject_token` submitted repeatedly, since nothing tracks consumption
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
