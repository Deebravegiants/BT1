# Q1690: get — rewrite is textual via body-type coupling

## Question
If an unprivileged attacker submits a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify` to `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input, does `Clients::Rest::Admin#get` end up acting on a value that was never authenticated, because the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#get`
- Entrypoint: `Rest::Admin#get(path:, body:, query:, headers:, tries:)` as called by host-app routes that derive `path` or `query` from request input
- Attacker controls: a nil body with a method that requires one, or a body supplied for a `:get`, probing `HttpRequest#verify`
- Exploit idea: the `.json` strip/append is a regex rewrite on a string that may already contain a query or fragment
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: table-driven test over crafted `path` values asserting the final URI always begins with `#{base_uri}/admin/api/#{version}/`
