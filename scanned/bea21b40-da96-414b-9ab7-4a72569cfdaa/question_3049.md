# Q3049: make_request — guard order via double .json

## Question
Can a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite, supplied by an unprivileged attacker at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, make `Clients::Rest::Admin#make_request` and the code consuming its result disagree, given that the `rest_disabled` and version-log branches run before the value that decides the URL is bounded? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a path already ending in `.json`, `.JSON` or `.json/`, exercising the strip-and-re-append rewrite
- Exploit idea: the `rest_disabled` and version-log branches run before the value that decides the URL is bounded
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
