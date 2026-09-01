# Q2883: covers? — parsing is lossy via case variance

## Question
Is there a reachable state in which an unprivileged attacker, controlling scope names differing only in case, since comparison is exact string set membership at `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation, makes `Auth::AuthScopes#covers?` return a result the caller treats as authenticated, given that splitting and stripping can merge or drop entries so the parsed set differs from the granted grant? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: scope names differing only in case, since comparison is exact string set membership
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
