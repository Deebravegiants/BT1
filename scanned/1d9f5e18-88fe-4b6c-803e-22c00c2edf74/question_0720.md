# Q720: == — session id published to the browser via cookie value

## Question
Is there a reachable state in which an unprivileged attacker, controlling the cookie value, which in the non-embedded callback branch is `session.id` itself at `SessionCookie#==`, which compares name, value and expiry, makes `Oauth::SessionCookie#==` return a result the caller treats as authenticated, given that in the non-embedded branch the cookie hands the storage key to the client? Test SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and quantify High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the cookie value, which in the non-embedded callback branch is `session.id` itself
- Exploit idea: in the non-embedded branch the cookie hands the storage key to the client
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: High - session fixation / forced OAuth completion binding a victim browser to an attacker-chosen shop (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
