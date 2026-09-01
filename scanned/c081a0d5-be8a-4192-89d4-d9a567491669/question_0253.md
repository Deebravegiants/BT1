# Q253: refresh_access_token — no shop/token binding via refresh token argument

## Question
Starting from `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`, can an unprivileged attacker supply the `refresh_token:` value, sent in the body to that host so that nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Auth::RefreshToken.refresh_access_token`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: the `refresh_token:` value, sent in the body to that host
- Exploit idea: nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the debug log emitted on failure contains neither the refresh token nor `client_secret`
