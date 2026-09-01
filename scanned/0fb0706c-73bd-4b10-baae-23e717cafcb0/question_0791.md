# Q791: begin_auth — state compared with == via host parameter

## Question
Can an unprivileged attacker reach `Oauth.begin_auth` through `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop` while supplying the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself, so that `state == auth_query.state` is a plain string comparison of a value the attacker can also observe or set, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself
- Exploit idea: `state == auth_query.state` is a plain string comparison of a value the attacker can also observe or set
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
