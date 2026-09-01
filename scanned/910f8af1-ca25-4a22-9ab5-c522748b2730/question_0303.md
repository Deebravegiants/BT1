# Q303: refresh_access_token — error logged with context via validator bypass string

## Question
Does `Auth::RefreshToken.refresh_access_token` collapse two distinct identities into one when an unprivileged attacker submits a shop string that passes `sanitize!` but resolves to an attacker host at `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`? Show that `Context.logger.debug` receives the upstream error message, which may embed request details, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a shop string that passes `sanitize!` but resolves to an attacker host
- Exploit idea: `Context.logger.debug` receives the upstream error message, which may embed request details
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: assert the refresh token is never sent to a host outside `TRUSTED_SHOPIFY_DOMAINS`
