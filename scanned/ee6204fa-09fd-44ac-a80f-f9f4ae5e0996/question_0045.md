# Q45: refresh_access_token — two credentials in one request via shop argument

## Question
If an unprivileged attacker submits the `shop:` argument, which decides the host that receives both `client_secret` and the refresh token to `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`, does `Auth::RefreshToken.refresh_access_token` end up acting on a value that was never authenticated, because the refresh token and `client_secret` travel together to a host derived from a caller-supplied string? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: the `shop:` argument, which decides the host that receives both `client_secret` and the refresh token
- Exploit idea: the refresh token and `client_secret` travel together to a host derived from a caller-supplied string
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: assert the refresh token is never sent to a host outside `TRUSTED_SHOPIFY_DOMAINS`
