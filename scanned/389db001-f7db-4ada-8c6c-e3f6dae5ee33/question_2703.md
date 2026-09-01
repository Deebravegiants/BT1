# Q2703: == — parsing is lossy via write_-shaped token

## Question
Starting from `AuthScopes#==` and `hash`, which compare only `compressed_scopes`, can an unprivileged attacker supply a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes` so that splitting and stripping can merge or drop entries so the parsed set differs from the granted grant? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Auth::AuthScopes#==`, and whether the result reaches High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
