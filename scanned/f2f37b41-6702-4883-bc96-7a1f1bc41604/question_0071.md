# Q71: refresh_access_token — error logged with context via shop/token mismatch

## Question
Starting from `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`, can an unprivileged attacker supply a `shop:` that does not correspond to the shop the refresh token was issued for so that `Context.logger.debug` receives the upstream error message, which may embed request details? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Auth::RefreshToken.refresh_access_token`, and whether the result reaches High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a `shop:` that does not correspond to the shop the refresh token was issued for
- Exploit idea: `Context.logger.debug` receives the upstream error message, which may embed request details
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a shop that differs from the token's issuing shop and assert the call raises rather than minting a mis-keyed session
