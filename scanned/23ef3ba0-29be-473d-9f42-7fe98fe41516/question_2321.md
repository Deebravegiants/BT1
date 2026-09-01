# Q2321: initialize — version chosen per call via tries argument

## Question
Can a `tries:` value that lengthens the retry loop around an authenticated request, supplied by an unprivileged attacker at `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, make `Clients::Rest::Admin#initialize` and the code consuming its result disagree, given that the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a `tries:` value that lengthens the retry loop around an authenticated request
- Exploit idea: the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
