# Q2529: get — version chosen per call via api_version override

## Question
Does `Clients::Rest::Admin#get` collapse two distinct identities into one when an unprivileged attacker submits an `api_version:` argument derived from request input, changing the base path and the loaded resource classes at `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input? Show that the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: an `api_version:` argument derived from request input, changing the base path and the loaded resource classes
- Exploit idea: the api-version override is per-instance and unvalidated against `SUPPORTED_ADMIN_VERSIONS` at this layer
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call `get(path: 'admin/oauth/access_token')` and assert the recorded URI, then assert the access token was not sent to it
