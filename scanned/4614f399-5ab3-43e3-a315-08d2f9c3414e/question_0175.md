# Q175: refresh_access_token — no shop/token binding via shop argument

## Question
Can an unprivileged attacker reach `Auth::RefreshToken.refresh_access_token` through `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)` while supplying the `shop:` argument, which decides the host that receives both `client_secret` and the refresh token, so that nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session, breaking the requirement that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: the `shop:` argument, which decides the host that receives both `client_secret` and the refresh token
- Exploit idea: nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the debug log emitted on failure contains neither the refresh token nor `client_secret`
