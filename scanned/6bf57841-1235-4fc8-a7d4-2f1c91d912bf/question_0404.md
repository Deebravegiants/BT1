# Q404: == — expiry advisory only via cookie name

## Question
Trace `Oauth::SessionCookie#==` from `SessionCookie#==`, which compares name, value and expiry with the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key: because `expires` is a browser hint; the callback never verifies freshness server-side, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key
- Exploit idea: `expires` is a browser hint; the callback never verifies freshness server-side
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
