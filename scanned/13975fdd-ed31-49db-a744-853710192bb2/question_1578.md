# Q1578: make_request — version chosen per call via query hash injection

## Question
If an unprivileged attacker submits a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query to the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, does `Clients::Rest::Admin#make_request` end up acting on a value that was never authenticated, because the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query
- Exploit idea: the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
