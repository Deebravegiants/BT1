# Q3060: initialize — rewrite is textual via double .json

## Question
Starting from `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, can an unprivileged attacker supply a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite so that the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `Clients::Rest::Admin#initialize`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite
- Exploit idea: the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
