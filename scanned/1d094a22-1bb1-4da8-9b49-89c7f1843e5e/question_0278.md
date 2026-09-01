# Q278: refresh_access_token — error logged with context via refresh token argument

## Question
Trace `Auth::RefreshToken.refresh_access_token` from `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)` with the `refresh_token:` value, sent in the body to that host: because `Context.logger.debug` receives the upstream error message, which may embed request details, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: the `refresh_token:` value, sent in the body to that host
- Exploit idea: `Context.logger.debug` receives the upstream error message, which may embed request details
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a shop that differs from the token's issuing shop and assert the call raises rather than minting a mis-keyed session
