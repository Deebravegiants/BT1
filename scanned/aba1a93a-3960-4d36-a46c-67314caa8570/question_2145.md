# Q2145: begin_auth — shop reaches HttpClient unvalidated via scope_override

## Question
If an unprivileged attacker submits the `scope_override:` argument or the `redirect_path:` argument if the host route derives either from request input to `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`, does `Oauth.begin_auth` end up acting on a value that was never authenticated, because `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: the `scope_override:` argument or the `redirect_path:` argument if the host route derives either from request input
- Exploit idea: `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
