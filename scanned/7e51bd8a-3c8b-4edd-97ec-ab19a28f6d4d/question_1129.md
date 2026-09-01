# Q1129: covers? — parsing is lossy via compressed vs expanded asymmetry

## Question
Does `Auth::AuthScopes#covers?` collapse two distinct identities into one when an unprivileged attacker submits a comparison where the caller's required scopes are compressed and the session's are expanded at `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation? Show that splitting and stripping can merge or drop entries so the parsed set differs from the granted grant, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
