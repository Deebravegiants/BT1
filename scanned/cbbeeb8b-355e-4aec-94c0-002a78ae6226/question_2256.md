# Q2256: initialize — version chosen per call via headers override

## Question
Does `Clients::Rest::Admin#initialize` collapse two distinct identities into one when an unprivileged attacker submits a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults at `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch? Show that the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults
- Exploit idea: the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
