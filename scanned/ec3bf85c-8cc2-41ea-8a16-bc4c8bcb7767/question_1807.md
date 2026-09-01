# Q1807: implied_scope — implication is textual via compressed vs expanded asymmetry

## Question
Starting from `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope, can an unprivileged attacker supply a comparison where the caller's required scopes are compressed and the session's are expanded so that `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Auth::AuthScopes#implied_scope`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#implied_scope`
- Entrypoint: `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
