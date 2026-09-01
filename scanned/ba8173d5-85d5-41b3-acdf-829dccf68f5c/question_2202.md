# Q2202: covers? — implication is textual via whitespace and empties

## Question
Can scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied, supplied by an unprivileged attacker at `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation, make `Auth::AuthScopes#covers?` and the code consuming its result disagree, given that `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
