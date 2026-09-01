# Q2082: == — parsing is lossy via scope string from a token response

## Question
If an unprivileged attacker submits the `scope` / `associated_user_scope` strings returned with an access token and stored on the session to `AuthScopes#==` and `hash`, which compare only `compressed_scopes`, does `Auth::AuthScopes#==` end up acting on a value that was never authenticated, because splitting and stripping can merge or drop entries so the parsed set differs from the granted grant? Close the question on AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: the `scope` / `associated_user_scope` strings returned with an access token and stored on the session
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
