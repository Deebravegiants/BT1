# Q2922: auth_base_uri — error path leaks via extra query parameters

## Question
If an unprivileged attacker submits additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`) to the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, does `Oauth.auth_base_uri` end up acting on a value that was never authenticated, because `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: additional query keys outside the five that `to_signable_string` covers (`code`, `host`, `shop`, `state`, `timestamp`)
- Exploit idea: `Errors::RequestAccessTokenError` and the HTTParty failure path surface response contents built from a request that carried `client_secret`
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
