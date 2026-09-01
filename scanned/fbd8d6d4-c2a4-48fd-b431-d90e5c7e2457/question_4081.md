# Q4081: get — prefix re-rooting via headers override

## Question
Can an unprivileged attacker reach `Clients::Rest::Admin#get` through `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input while supplying a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults, so that the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host?

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults
- Exploit idea: the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
