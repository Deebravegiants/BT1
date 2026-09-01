# Q2727: == — asymmetric comparison via compressed vs expanded asymmetry

## Question
Can a comparison where the caller's required scopes are compressed and the session's are expanded, supplied by an unprivileged attacker at `AuthScopes#==` and `hash`, which compare only `compressed_scopes`, make `Auth::AuthScopes#==` and the code consuming its result disagree, given that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
