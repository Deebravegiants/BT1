# Q2137: make_request — caller headers win via query hash injection

## Question
Does `Clients::Rest::Admin#make_request` collapse two distinct identities into one when an unprivileged attacker submits a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query at the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`? Show that `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a `query:` hash whose keys or values are user-controlled and are serialised by HTTParty into the outgoing query
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
