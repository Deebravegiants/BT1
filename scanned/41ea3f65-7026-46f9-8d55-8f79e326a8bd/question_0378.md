# Q378: refresh_access_token — no shop/token binding via validator bypass string

## Question
Can an unprivileged attacker reach `Auth::RefreshToken.refresh_access_token` through `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)` while supplying a shop string that passes `sanitize!` but resolves to an attacker host, so that nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a shop string that passes `sanitize!` but resolves to an attacker host
- Exploit idea: nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: assert the refresh token is never sent to a host outside `TRUSTED_SHOPIFY_DOMAINS`
