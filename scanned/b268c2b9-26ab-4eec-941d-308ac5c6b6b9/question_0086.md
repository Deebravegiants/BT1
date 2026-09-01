# Q86: exchange_token — client_secret sent to a derived host via non-embedded / private config

## Question
Does `TokenExchange.exchange_token` collapse two distinct identities into one when an unprivileged attacker submits an app configuration that flips the `Context.private?` and `Context.embedded?` guards at `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token? Show that the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: an app configuration that flips the `Context.private?` and `Context.embedded?` guards
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
