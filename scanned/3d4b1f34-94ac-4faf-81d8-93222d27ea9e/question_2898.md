# Q2898: begin_auth — shop reaches HttpClient unvalidated via host parameter

## Question
Can an unprivileged attacker reach `Oauth.begin_auth` through `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop` while supplying the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself, so that `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`)?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: the base64 `host` parameter, which is signed but never validated as a Shopify admin host before the app uses it to frame itself
- Exploit idea: `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
