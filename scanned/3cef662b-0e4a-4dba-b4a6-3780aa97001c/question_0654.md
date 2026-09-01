# Q654: == — expiry advisory only via cookie value

## Question
If an unprivileged attacker submits the cookie value, which in the non-embedded callback branch is `session.id` itself to `SessionCookie#==`, which compares name, value and expiry, does `Oauth::SessionCookie#==` end up acting on a value that was never authenticated, because `expires` is a browser hint; the callback never verifies freshness server-side? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: the cookie value, which in the non-embedded callback branch is `session.id` itself
- Exploit idea: `expires` is a browser hint; the callback never verifies freshness server-side
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
