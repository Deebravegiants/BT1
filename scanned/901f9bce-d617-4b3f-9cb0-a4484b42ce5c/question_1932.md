# Q1932: initialize — equality ignores expansion via compressed vs expanded asymmetry

## Question
Can an unprivileged attacker reach `Auth::AuthScopes#initialize` through `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation while supplying a comparison where the caller's required scopes are compressed and the session's are expanded, so that `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal, breaking the requirement that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
