# Q3390: make_request — caller headers win via tries argument

## Question
Does `Clients::Rest::Admin#make_request` collapse two distinct identities into one when an unprivileged attacker submits a `tries:` value that lengthens the retry loop around an authenticated request at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`? Show that `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a `tries:` value that lengthens the retry loop around an authenticated request
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
