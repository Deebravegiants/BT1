# Q3286: begin_auth — shop reaches HttpClient unvalidated via stale timestamp

## Question
If an unprivileged attacker submits a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now` to `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`, does `Oauth.begin_auth` end up acting on a value that was never authenticated, because `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: a signed callback whose `timestamp` is arbitrarily old, since nothing compares it to `Time.now`
- Exploit idea: `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
