# Q201: refresh_access_token — two credentials in one request via validator bypass string

## Question
Trace `Auth::RefreshToken.refresh_access_token` from `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)` with a shop string that passes `sanitize!` but resolves to an attacker host: because the refresh token and `client_secret` travel together to a host derived from a caller-supplied string, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a shop string that passes `sanitize!` but resolves to an attacker host
- Exploit idea: the refresh token and `client_secret` travel together to a host derived from a caller-supplied string
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: assert the refresh token is never sent to a host outside `TRUSTED_SHOPIFY_DOMAINS`
