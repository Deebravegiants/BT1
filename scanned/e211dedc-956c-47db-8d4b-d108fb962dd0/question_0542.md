# Q542: implied_scope — no vocabulary validation via compressed vs expanded asymmetry

## Question
If an unprivileged attacker submits a comparison where the caller's required scopes are compressed and the session's are expanded to `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope, does `Auth::AuthScopes#implied_scope` end up acting on a value that was never authenticated, because any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#implied_scope`
- Entrypoint: `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
