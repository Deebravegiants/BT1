# Q3352: validate_auth_callback — private-app guard ordering via expired cookie

## Question
Is there a reachable state in which an unprivileged attacker, controlling a `SessionCookie` presented after its 60-second `expires` has passed, which the gem never re-checks on the callback side at `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route, makes `Oauth.validate_auth_callback` return a result the caller treats as authenticated, given that `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host? Test SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: a `SessionCookie` presented after its 60-second `expires` has passed, which the gem never re-checks on the callback side
- Exploit idea: `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `begin_auth(shop: 'a.myshopify.com')`, then `validate_auth_callback` with a validly signed query naming shop B, and assert the returned `session.shop`
