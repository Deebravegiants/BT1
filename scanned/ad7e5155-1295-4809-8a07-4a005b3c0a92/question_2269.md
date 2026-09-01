# Q2269: request_url — prefix re-rooting via headers override

## Question
Starting from the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`, can an unprivileged attacker supply a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults so that the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Clients::Rest::Admin#request_url`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#request_url`
- Entrypoint: the protected `request_url`, which strips a leading `/` and a trailing `.json`, re-appends `.json`, and re-roots at `@base_uri` for any path starting with `admin/`
- Attacker controls: a `headers:` hash that reaches `extra_headers` and is merged over the client's defaults
- Exploit idea: the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
