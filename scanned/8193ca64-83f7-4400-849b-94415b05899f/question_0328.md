# Q328: refresh_access_token — two credentials in one request via shop/token mismatch

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `shop:` that does not correspond to the shop the refresh token was issued for at `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`, makes `Auth::RefreshToken.refresh_access_token` return a result the caller treats as authenticated, given that the refresh token and `client_secret` travel together to a host derived from a caller-supplied string? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's refresh token, granting durable access after rotation.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a `shop:` that does not correspond to the shop the refresh token was issued for
- Exploit idea: the refresh token and `client_secret` travel together to a host derived from a caller-supplied string
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's refresh token, granting durable access after rotation (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the debug log emitted on failure contains neither the refresh token nor `client_secret`
