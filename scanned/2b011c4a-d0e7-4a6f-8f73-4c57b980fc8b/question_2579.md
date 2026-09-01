# Q2579: initialize — caller headers win via path prefix admin/

## Question
If an unprivileged attacker submits a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely to `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, does `Clients::Rest::Admin#initialize` end up acting on a value that was never authenticated, because `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults? Close the question on SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a `path` beginning with `admin/`, which bypasses the `/admin/api/<version>` base path entirely
- Exploit idea: `extra_headers` merges last inside `HttpClient#request`, overriding security-relevant defaults
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
