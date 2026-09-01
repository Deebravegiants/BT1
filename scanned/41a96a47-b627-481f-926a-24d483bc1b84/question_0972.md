# Q972: implied_scope — parsing is lossy via scope string from a token response

## Question
Is there a reachable state in which an unprivileged attacker, controlling the `scope` / `associated_user_scope` strings returned with an access token and stored on the session at `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope, makes `Auth::AuthScopes#implied_scope` return a result the caller treats as authenticated, given that splitting and stripping can merge or drop entries so the parsed set differs from the granted grant? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#implied_scope`
- Entrypoint: `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope
- Attacker controls: the `scope` / `associated_user_scope` strings returned with an access token and stored on the session
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
