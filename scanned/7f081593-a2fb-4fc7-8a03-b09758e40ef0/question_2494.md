# Q2494: == — asymmetric comparison via unauthenticated_ prefix

## Question
Does `Auth::AuthScopes#==` collapse two distinct identities into one when an unprivileged attacker submits an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*` at `AuthScopes#==` and `hash`, which compare only `compressed_scopes`? Show that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
