# Q301: implied_scope — asymmetric comparison via delimiter in a scope name

## Question
Can an unprivileged attacker reach `Auth::AuthScopes#implied_scope` through `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope while supplying a scope name containing `,` so one entry becomes two, so that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in Critical - cross-tenant access: one shop's request reads or mutates another merchant's data?

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#implied_scope`
- Entrypoint: `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope
- Attacker controls: a scope name containing `,` so one entry becomes two
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
