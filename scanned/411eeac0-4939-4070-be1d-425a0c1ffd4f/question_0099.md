# Q99: Oauth::SessionCookie — one cookie, two meanings via expiry

## Question
Starting from `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, can an unprivileged attacker supply the 60-second `expires` set at `begin_auth`, which the callback never re-checks so that the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other? Determine whether SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` still holds through `Oauth::SessionCookie`, and whether the result reaches Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the 60-second `expires` set at `begin_auth`, which the callback never re-checks
- Exploit idea: the same cookie name carries the pre-auth nonce and the post-auth session id, so a value from one phase is accepted in the other
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the cookie issued by `begin_auth` cannot be replayed after its `expires` has passed
