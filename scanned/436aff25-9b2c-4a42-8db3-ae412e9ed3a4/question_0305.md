# Q305: Oauth::SessionCookie — session id published to the browser via cookie name

## Question
Can the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key, supplied by an unprivileged attacker at `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, make `Oauth::SessionCookie` and the code consuming its result disagree, given that in the non-embedded branch the cookie hands the storage key to the client? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the fixed `SESSION_COOKIE_NAME`, shared by the OAuth nonce and the post-auth session key
- Exploit idea: in the non-embedded branch the cookie hands the storage key to the client
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert the cookie issued by `begin_auth` cannot be replayed after its `expires` has passed
