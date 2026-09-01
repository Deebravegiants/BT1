# Q3258: initialize — caller headers win via traversal to another version

## Question
If an unprivileged attacker submits `../<other version>/` segments that move the request to an API version the app did not configure to `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, does `Clients::Rest::Admin#initialize` end up acting on a value that was never authenticated, because `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: `../<other version>/` segments that move the request to an API version the app did not configure
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
