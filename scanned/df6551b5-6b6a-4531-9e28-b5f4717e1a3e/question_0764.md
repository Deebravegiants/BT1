# Q764: == — one cookie, two meanings via attacker-set cookie

## Question
Starting from `SessionCookie#==`, which compares name, value and expiry, can an unprivileged attacker supply a cookie the attacker plants in the victim's browser before the OAuth flow begins so that the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Oauth::SessionCookie#==`, and whether the result reaches High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: a cookie the attacker plants in the victim's browser before the OAuth flow begins
- Exploit idea: the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
