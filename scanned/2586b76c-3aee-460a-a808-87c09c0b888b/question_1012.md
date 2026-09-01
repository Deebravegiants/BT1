# Q1012: store_scopes — no vocabulary validation via write_-shaped token

## Question
Can a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`, supplied by an unprivileged attacker at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, make `Auth::AuthScopes#store_scopes` and the code consuming its result disagree, given that any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
