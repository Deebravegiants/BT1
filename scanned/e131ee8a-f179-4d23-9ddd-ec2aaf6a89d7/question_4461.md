# Q4461: validate_auth_callback — redirect target unbound via host parameter

## Question
Does `Oauth.validate_auth_callback` collapse two distinct identities into one when an unprivileged attacker submits the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself at `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route? Show that `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself
- Exploit idea: `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
