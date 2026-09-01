# Q1826: begin_auth — cookie carries no shop via chosen state cookie

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely at `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`, makes `Oauth.begin_auth` return a result the caller treats as authenticated, given that `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: the `shopify_app_session` cookie value, set by the attacker in the victim's browser or omitted entirely
- Exploit idea: `SessionCookie` holds only the nonce - not the shop, `is_online` flag or scope that `begin_auth` was called with, so the callback cannot detect a shop swap
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
