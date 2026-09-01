# Q19: refresh_access_token — two credentials in one request via error path

## Question
Trace `Auth::RefreshToken.refresh_access_token` from `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)` with a failing upstream response, whose message reaches `Context.logger.debug` before the error is re-raised: because the refresh token and `client_secret` travel together to a host derived from a caller-supplied string, does the value that was verified stop being the value that is used? Prove the break against SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and map it to High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a failing upstream response, whose message reaches `Context.logger.debug` before the error is re-raised
- Exploit idea: the refresh token and `client_secret` travel together to a host derived from a caller-supplied string
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the debug log emitted on failure contains neither the refresh token nor `client_secret`
