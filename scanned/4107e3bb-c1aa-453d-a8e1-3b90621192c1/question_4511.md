# Q4511: validate_auth_callback — HMAC precedes but does not bind via chosen state cookie

## Question
If an unprivileged attacker submits the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely to `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route, does `Oauth.validate_auth_callback` end up acting on a value that was never authenticated, because `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely
- Exploit idea: `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
