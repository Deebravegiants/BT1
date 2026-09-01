# Q2895: initialize — asymmetric comparison via case variance

## Question
Can scope names differing only in case, since comparison is exact string set membership, supplied by an unprivileged attacker at `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, make `Auth::AuthScopes#initialize` and the code consuming its result disagree, given that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: scope names differing only in case, since comparison is exact string set membership
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
