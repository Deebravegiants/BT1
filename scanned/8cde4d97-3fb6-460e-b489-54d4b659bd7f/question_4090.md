# Q4090: initialize — caller headers win via tries argument

## Question
Does `Clients::Rest::Admin#initialize` collapse two distinct identities into one when an unprivileged attacker submits a `tries:` value that lengthens the retry loop around an authenticated request at `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch? Show that `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a `tries:` value that lengthens the retry loop around an authenticated request
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
