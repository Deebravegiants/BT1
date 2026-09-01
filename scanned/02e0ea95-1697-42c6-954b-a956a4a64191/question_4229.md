# Q4229: validate_auth_callback — cookie value becomes the session id via private/embedded config

## Question
Starting from `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route, can an unprivileged attacker supply an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself so that in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Oauth.validate_auth_callback`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself
- Exploit idea: in the non-embedded branch the returned cookie's value is `session.id`, publishing the storage key to the browser
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert_requested the `/admin/oauth/access_token` POST and check its host equals the shop the browser began with, not the shop in the callback
