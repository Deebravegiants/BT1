# Q73: Oauth::SessionCookie — no shop or scope in the cookie via cookie value

## Question
If an unprivileged attacker submits the cookie value, which in the non-embedded callback branch is `session.id` itself to `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, does `Oauth::SessionCookie` end up acting on a value that was never authenticated, because the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the cookie value, which in the non-embedded callback branch is `session.id` itself
- Exploit idea: the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the cookie issued by `begin_auth` cannot be replayed after its `expires` has passed
