# Q1309: covers? — asymmetric comparison via compressed vs expanded asymmetry

## Question
Can an unprivileged attacker reach `Auth::AuthScopes#covers?` through `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation while supplying a comparison where the caller's required scopes are compressed and the session's are expanded, so that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
