# Q2286: store_scopes — asymmetric comparison via compressed vs expanded asymmetry

## Question
Can a comparison where the caller's required scopes are compressed and the session's are expanded, supplied by an unprivileged attacker at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, make `Auth::AuthScopes#store_scopes` and the code consuming its result disagree, given that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
