# Q4121: validate_auth_callback — cookie carries no shop via stale timestamp

## Question
Trace `Oauth.validate_auth_callback` from `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route with a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now`: because `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap, does the value that was verified stop being the value that is used? Prove the break against CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and map it to High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now`
- Exploit idea: `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
