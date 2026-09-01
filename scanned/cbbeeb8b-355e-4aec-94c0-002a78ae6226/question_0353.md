# Q353: refresh_access_token — error logged with context via error path

## Question
If an unprivileged attacker submits a failing upstream response, whose message reaches `Context.logger.debug` before the error is re-raised to `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`, does `Auth::RefreshToken.refresh_access_token` end up acting on a value that was never authenticated, because `Context.logger.debug` receives the upstream error message, which may embed request details? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a failing upstream response, whose message reaches `Context.logger.debug` before the error is re-raised
- Exploit idea: `Context.logger.debug` receives the upstream error message, which may embed request details
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a shop that differs from the token's issuing shop and assert the call raises rather than minting a mis-keyed session
