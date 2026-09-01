# Q762: store_scopes — equality ignores expansion via compressed vs expanded asymmetry

## Question
Is there a reachable state in which an unprivileged attacker, controlling a comparison where the caller's required scopes are compressed and the session's are expanded at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, makes `Auth::AuthScopes#store_scopes` return a result the caller treats as authenticated, given that `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
