# Q925: make_request — caller headers win via case-varied prefix

## Question
Starting from the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`, can an unprivileged attacker supply a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip so that `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Clients::Rest::Admin#make_request`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#make_request`
- Entrypoint: the private `make_request`, which sets `body_type` from whether `body` is nil and forwards `headers` as `extra_headers`
- Attacker controls: a path beginning with `Admin/` or `/admin/`, probing the exact `start_with?("admin/")` comparison after the leading-slash strip
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
