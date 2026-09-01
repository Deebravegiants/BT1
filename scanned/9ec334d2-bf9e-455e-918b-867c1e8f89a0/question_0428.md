# Q428: == — no shop or scope in the cookie via cookie name

## Question
Starting from `SessionCookie#==`, which compares name, value and expiry, can an unprivileged attacker supply the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key so that the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Oauth::SessionCookie#==`, and whether the result reaches High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key
- Exploit idea: the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
