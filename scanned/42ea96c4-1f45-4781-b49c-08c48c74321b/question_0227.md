# Q227: refresh_access_token — no shop/token binding via shop/token mismatch

## Question
If an unprivileged attacker submits a `shop:` that does not correspond to the shop the refresh token was issued for to `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`, does `Auth::RefreshToken.refresh_access_token` end up acting on a value that was never authenticated, because nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a `shop:` that does not correspond to the shop the refresh token was issued for
- Exploit idea: nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a shop that differs from the token's issuing shop and assert the call raises rather than minting a mis-keyed session
