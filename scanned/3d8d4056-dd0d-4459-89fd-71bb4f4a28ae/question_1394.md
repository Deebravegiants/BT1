# Q1394: validate_auth_callback — redirect target unbound via private/embedded config

## Question
Starting from `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route, can an unprivileged attacker supply an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself so that `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Oauth.validate_auth_callback`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: an app configured with `is_embedded: false`, where the callback returns a cookie whose value is `session.id` itself
- Exploit idea: `redirect_uri` is built from `Context.host` + `redirect_path` at authorize time but never re-verified at callback time
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
