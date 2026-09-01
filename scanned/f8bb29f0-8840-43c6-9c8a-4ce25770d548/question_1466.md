# Q1466: initialize — caller headers win via resource id injection

## Question
If an unprivileged attacker submits an id segment taken from user input, e.g. `orders/#{params[:id]}` where the id contains `/` or `?` to `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, does `Clients::Rest::Admin#initialize` end up acting on a value that was never authenticated, because `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: an id segment taken from user input, e.g. `orders/#{params[:id]}` where the id contains `/` or `?`
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
