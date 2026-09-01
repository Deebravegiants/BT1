# Q2325: covers? — no vocabulary validation via compressed vs expanded asymmetry

## Question
Starting from `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation, can an unprivileged attacker supply a comparison where the caller's required scopes are compressed and the session's are expanded so that any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Auth::AuthScopes#covers?`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
