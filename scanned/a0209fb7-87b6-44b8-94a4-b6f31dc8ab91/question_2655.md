# Q2655: covers? — asymmetric comparison via unauthenticated_ prefix

## Question
Does `Auth::AuthScopes#covers?` collapse two distinct identities into one when an unprivileged attacker submits an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*` at `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation? Show that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
