# Q2754: validate_auth_callback — shop reaches HttpClient unvalidated via duplicated query keys

## Question
If an unprivileged attacker submits repeated `shop=`/`state=` keys where the framework's last-wins parse differs from the value that was signed to `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route, does `Oauth.validate_auth_callback` end up acting on a value that was never authenticated, because `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: repeated `shop=`/`state=` keys where the framework's last-wins parse differs from the value that was signed
- Exploit idea: `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
