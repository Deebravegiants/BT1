# Q125: Oauth::SessionCookie — no shop or scope in the cookie via expiry

## Question
Is there a reachable state in which an unprivileged attacker, controlling the 60-second `expires` set at `begin_auth`, which the callback never re-checks at `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, makes `Oauth::SessionCookie` return a result the caller treats as authenticated, given that the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the 60-second `expires` set at `begin_auth`, which the callback never re-checks
- Exploit idea: the struct carries nothing that binds the nonce to the shop, the online flag or the scope it was issued for
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the cookie issued by `begin_auth` cannot be replayed after its `expires` has passed
