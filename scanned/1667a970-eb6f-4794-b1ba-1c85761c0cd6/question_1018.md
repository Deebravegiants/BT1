# Q1018: auth_base_uri — HMAC precedes but does not bind via attacker-signed callback

## Question
If an unprivileged attacker submits a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app to the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`, does `Oauth.auth_base_uri` end up acting on a value that was never authenticated, because `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization? Close the question on SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth.rb` -> `Oauth.auth_base_uri`
- Entrypoint: the private `auth_base_uri(shop)` that builds `"https://#{shop}/admin"` with no call to `ShopValidator`
- Attacker controls: a full OAuth callback that Shopify validly signed for the attacker's own development shop, replayed against the victim app
- Exploit idea: `HmacValidator.validate(auth_query)` proves Shopify signed those five fields, not that this browser began this authorization
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: replay the same signed `auth_query` twice and assert the second call raises rather than minting a second session
