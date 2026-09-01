# Q1362: auth_base_uri — shop reaches HttpClient unvalidated via attacker-signed callback

## Question
Can a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app, supplied by an unprivileged attacker at the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, make `Oauth.auth_base_uri` and the code consuming its result disagree, given that `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app
- Exploit idea: `Session.new(shop: auth_query.shop)` becomes `@base_uri = "https://#{session.shop}"` for the POST that carries `client_id` and `client_secret`
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
