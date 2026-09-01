# Q2607: covers? — equality ignores expansion via case variance

## Question
If an unprivileged attacker submits scope names differing only in case, since comparison is exact string set membership to `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation, does `Auth::AuthScopes#covers?` end up acting on a value that was never authenticated, because `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: scope names differing only in case, since comparison is exact string set membership
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
