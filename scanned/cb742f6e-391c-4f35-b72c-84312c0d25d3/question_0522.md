# Q522: Oauth::SessionCookie — one cookie, two meanings via attacker-set cookie

## Question
Can a cookie the attacker plants in the victim's browser before the OAuth flow begins, supplied by an unprivileged attacker at `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, make `Oauth::SessionCookie` and the code consuming its result disagree, given that the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: a cookie the attacker plants in the victim's browser before the OAuth flow begins
- Exploit idea: the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
