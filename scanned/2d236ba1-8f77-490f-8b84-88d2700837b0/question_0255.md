# Q255: Oauth::SessionCookie — expiry advisory only via cookie value

## Question
If an unprivileged attacker submits the cookie value, which in the non-embedded callback branch is `session.id` itself to `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, does `Oauth::SessionCookie` end up acting on a value that was never authenticated, because `expires` is a browser hint; the callback never verifies freshness server-side? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the cookie value, which in the non-embedded callback branch is `session.id` itself
- Exploit idea: `expires` is a browser hint; the callback never verifies freshness server-side
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the cookie issued by `begin_auth` cannot be replayed after its `expires` has passed
