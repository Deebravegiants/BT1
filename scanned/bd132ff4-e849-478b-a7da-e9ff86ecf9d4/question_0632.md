# Q632: Oauth::SessionCookie — expiry advisory only via expiry

## Question
Does `Oauth::SessionCookie` collapse two distinct identities into one when an unprivileged attacker submits the 60-second `expires` set at `begin_auth`, which the callback never re-checks at `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`? Show that `expires` is a browser hint; the callback never verifies freshness server-side, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the 60-second `expires` set at `begin_auth`, which the callback never re-checks
- Exploit idea: `expires` is a browser hint; the callback never verifies freshness server-side
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
