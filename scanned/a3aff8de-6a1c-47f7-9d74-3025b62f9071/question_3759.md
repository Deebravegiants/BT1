# Q3759: validate_auth_callback — HMAC precedes but does not bind via attacker-signed callback

## Question
Can an unprivileged attacker reach `Oauth.validate_auth_callback` through `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route while supplying a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app, so that `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app?

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app
- Exploit idea: `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the returned `SessionCookie#value` is never equal to `session.id` for an embedded app, and that the cookie is cleared
