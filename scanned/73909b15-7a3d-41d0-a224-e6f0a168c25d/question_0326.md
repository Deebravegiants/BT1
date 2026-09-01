# Q326: initialize — no vocabulary validation via compressed vs expanded asymmetry

## Question
Can a comparison where the caller's required scopes are compressed and the session's are expanded, supplied by an unprivileged attacker at `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, make `Auth::AuthScopes#initialize` and the code consuming its result disagree, given that any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued? The binding to test is AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
