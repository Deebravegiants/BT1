# Q3939: begin_auth — error path leaks via extra query parameters

## Question
Trace `Oauth.begin_auth` from `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop` with additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`): because `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.begin_auth`
- Entrypoint: `ShopifyAPI::Auth::Oauth.begin_auth(shop:, redirect_path:, is_online:, scope_override:)`, reached from the app's install/login route with a user-supplied `shop`
- Attacker controls: additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`)
- Exploit idea: `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
