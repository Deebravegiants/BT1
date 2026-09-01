# Q2232: covers? — asymmetric comparison via write_-shaped token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes` at `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation, makes `Auth::AuthScopes#covers?` return a result the caller treats as authenticated, given that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
