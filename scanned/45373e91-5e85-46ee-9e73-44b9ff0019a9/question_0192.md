# Q192: make_request — rewrite is textual via body-type coupling

## Question
If an unprivileged attacker submits a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify` to the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, does `Clients::Rest::Admin#make_request` end up acting on a value that was never authenticated, because the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify`
- Exploit idea: the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
