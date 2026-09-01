# Q1165: covers? — implication is textual via compressed vs expanded asymmetry

## Question
If an unprivileged attacker submits a comparison where the caller's required scopes are compressed and the session's are expanded to `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation, does `Auth::AuthScopes#covers?` end up acting on a value that was never authenticated, because `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
