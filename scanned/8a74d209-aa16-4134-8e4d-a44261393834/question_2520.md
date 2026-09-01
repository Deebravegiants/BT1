# Q2520: == — implication is textual via compressed vs expanded asymmetry

## Question
Can an unprivileged attacker reach `Auth::AuthScopes#==` through `AuthScopes#==` and `hash`, which compare only `compressed_scopes` while supplying a comparison where the caller's required scopes are compressed and the session's are expanded, so that `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
