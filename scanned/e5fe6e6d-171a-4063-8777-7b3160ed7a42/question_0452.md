# Q452: Oauth::SessionCookie — one cookie, two meanings via cookie value

## Question
Can the cookie value, which in the non-embedded callback branch is `session.id` itself, supplied by an unprivileged attacker at `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, make `Oauth::SessionCookie` and the code consuming its result disagree, given that the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the cookie value, which in the non-embedded callback branch is `session.id` itself
- Exploit idea: the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
