# Q3954: make_request — rewrite is textual via double .json

## Question
Is there a reachable state in which an unprivileged attacker, controlling a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, makes `Clients::Rest::Admin#make_request` return a result the caller treats as authenticated, given that the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite
- Exploit idea: the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
