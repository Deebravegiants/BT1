# Q4166: begin_auth — redirect target unbound via stale timestamp

## Question
Starting from `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`, can an unprivileged attacker supply a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now` so that `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Oauth.begin_auth`, and whether the result reaches High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now`
- Exploit idea: `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
