# Q1111: initialize — asymmetric comparison via whitespace and empties

## Question
Trace `Auth::AuthScopes#initialize` from `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation with scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied: because `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
