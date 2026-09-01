# Q123: refresh_access_token — no shop/token binding via error path

## Question
Can a failing upstream response, whose message reaches `Context.logger.debug` before the error is re-raised, supplied by an unprivileged attacker at `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`, make `Auth::RefreshToken.refresh_access_token` and the code consuming its result disagree, given that nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session? The binding to test is CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted; the impact to prove is High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/auth/refresh_token.rb` -> `Auth::RefreshToken.refresh_access_token`
- Entrypoint: `ShopifyAPI::Auth::RefreshToken.refresh_access_token(shop:, refresh_token:)`
- Attacker controls: a failing upstream response, whose message reaches `Context.logger.debug` before the error is re-raised
- Exploit idea: nothing checks that the refresh token belongs to the named shop, so a mismatch silently re-keys the resulting session
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: assert the refresh token is never sent to a host outside `TRUSTED_SHOPIFY_DOMAINS`
