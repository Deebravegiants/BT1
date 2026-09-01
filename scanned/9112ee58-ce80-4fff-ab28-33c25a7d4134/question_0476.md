# Q476: == — no shop or scope in the cookie via expiry

## Question
Can an unprivileged attacker reach `Oauth::SessionCookie#==` through `SessionCookie#==`, which compares name, value and expiry while supplying the 60-second `expires` set at `begin_auth`, which the callback never re-checks, so that the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop?

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the 60-second `expires` set at `begin_auth`, which the callback never re-checks
- Exploit idea: the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
