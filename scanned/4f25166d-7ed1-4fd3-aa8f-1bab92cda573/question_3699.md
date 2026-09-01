# Q3699: begin_auth — cookie carries no shop via duplicated query keys

## Question
If an unprivileged attacker submits repeated `shop=`/`state=` keys where the framework's last-wins parse differs from the value that was signed to `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`, does `Oauth.begin_auth` end up acting on a value that was never authenticated, because `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: repeated `shop=`/`state=` keys where the framework's last-wins parse differs from the value that was signed
- Exploit idea: `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
