# Q1471: initialize — asymmetric comparison via unauthenticated_ prefix

## Question
Starting from `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, can an unprivileged attacker supply an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*` so that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Auth::AuthScopes#initialize`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
