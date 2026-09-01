# Q586: covers? — implication is textual via unauthenticated_ prefix

## Question
Trace `Auth::AuthScopes#covers?` from `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation with an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`: because `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes, does the value that was verified stop being the value that is used? Prove the break against AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
