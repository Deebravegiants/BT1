# Q3572: validate_auth_callback — private-app guard ordering via cross-shop state reuse

## Question
Does `Oauth.validate_auth_callback` collapse two distinct identities into one when an unprivileged attacker submits a `state` nonce obtained from the attacker's own `begin_auth` call and presented with a callback naming a different `shop` at `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route? Show that `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.validate_auth_callback`
- Entrypoint: `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, reached from the app's public OAuth callback route
- Attacker controls: a `state` nonce obtained from the attacker's own `begin_auth` call and presented with a callback naming a different `shop`
- Exploit idea: `Context.private?` and `Context.setup?` are checked around, not before, the value that decides the outbound host
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `begin_auth(shop: 'a.myshopify.com')`, then `validate_auth_callback` with a validly signed query naming shop B, and assert the returned `session.shop`
