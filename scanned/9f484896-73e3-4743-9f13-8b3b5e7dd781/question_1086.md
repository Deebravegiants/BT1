# Q1086: get — caller headers win via body-type coupling

## Question
Starting from `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input, can an unprivileged attacker supply a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify` so that `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Clients::Rest::Admin#get`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify`
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
