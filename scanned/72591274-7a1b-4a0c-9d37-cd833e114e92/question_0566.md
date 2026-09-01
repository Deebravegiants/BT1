# Q566: == — no shop or scope in the cookie via cookie value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the cookie value, which in the non-embedded callback branch is `session.id` itself at `SessionCookie#==`, which compares name, value and expiry, makes `Oauth::SessionCookie#==` return a result the caller treats as authenticated, given that the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the cookie value, which in the non-embedded callback branch is `session.id` itself
- Exploit idea: the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
