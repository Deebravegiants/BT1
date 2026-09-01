# Q1072: covers? — parsing is lossy via write_-shaped token

## Question
Starting from `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation, can an unprivileged attacker supply a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes` so that splitting and stripping can merge or drop entries so the parsed set differs from the granted grant? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Auth::AuthScopes#covers?`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `AuthScopes.new('write_x').covers?(AuthScopes.new('read_x'))` cannot be reached with a fabricated `x`
