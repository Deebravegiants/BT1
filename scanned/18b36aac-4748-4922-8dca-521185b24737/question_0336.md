# Q336: validate_auth_callback — HMAC precedes but does not bind via host parameter

## Question
Can an unprivileged attacker reach `Oauth.validate_auth_callback` through `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route while supplying the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself, so that `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself
- Exploit idea: `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `begin_auth(shop: 'a.myshopify.com')`, then `validate_auth_callback` with a validly signed query naming shop B, and assert the returned `session.shop`
