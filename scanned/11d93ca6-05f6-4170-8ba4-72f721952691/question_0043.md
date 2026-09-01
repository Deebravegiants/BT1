# Q43: implied_scope — equality ignores expansion via whitespace and empties

## Question
Starting from `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope, can an unprivileged attacker supply scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied so that `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Auth::AuthScopes#implied_scope`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#implied_scope`
- Entrypoint: `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope
- Attacker controls: scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
