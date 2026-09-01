# Q151: == — expiry advisory only via attacker-set cookie

## Question
Can a cookie the attacker plants in the victim's browser before the OAuth flow begins, supplied by an unprivileged attacker at `SessionCookie#==`, which compares name, value and expiry, make `Oauth::SessionCookie#==` and the code consuming its result disagree, given that `expires` is a browser hint; the callback never verifies freshness server-side? The binding to test is SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie#==`
- Entrypoint: `SessionCookie#==`, which compares name, value and expiry
- Attacker controls: a cookie the attacker plants in the victim's browser before the OAuth flow begins
- Exploit idea: `expires` is a browser hint; the callback never verifies freshness server-side
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the cookie issued by `begin_auth` cannot be replayed after its `expires` has passed
