# Q3495: begin_auth — no replay window via host parameter

## Question
Does `Oauth.begin_auth` collapse two distinct identities into one when an unprivileged attacker submits the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself at `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`? Show that nothing records that a `state` was consumed, so a signed callback can be submitted repeatedly, that SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host is violated, and that the consequence is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself
- Exploit idea: nothing records that a `state` was consumed, so a signed callback can be submitted repeatedly
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
