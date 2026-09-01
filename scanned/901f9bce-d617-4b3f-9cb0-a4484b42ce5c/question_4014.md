# Q4014: make_request — guard order via headers override

## Question
If an unprivileged attacker submits a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults to the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, does `Clients::Rest::Admin#make_request` end up acting on a value that was never authenticated, because the `rest_disabled` and version-log branches run before the value that decides the URL is bounded? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
