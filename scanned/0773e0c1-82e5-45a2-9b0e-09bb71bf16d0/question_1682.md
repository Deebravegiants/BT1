# Q1682: auth_base_uri — error path leaks via attacker-signed callback

## Question
Does `Oauth.auth_base_uri` collapse two distinct identities into one when an unprivileged attacker submits a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app at the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`? Show that `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app
- Exploit idea: `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
