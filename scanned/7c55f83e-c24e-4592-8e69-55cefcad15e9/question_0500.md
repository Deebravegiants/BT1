# Q500: == — session id published to the browser via cookie name

## Question
If an unprivileged attacker submits the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key to `SessionCookie#==`, which compares name, value and expiry, does `Oauth::SessionCookie#==` end up acting on a value that was never authenticated, because in the non-embedded branch the cookie hands the storage key to the client? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key
- Exploit idea: in the non-embedded branch the cookie hands the storage key to the client
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
