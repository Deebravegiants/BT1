# Q95: initialize — equality ignores expansion via unauthenticated_ prefix

## Question
Can an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`, supplied by an unprivileged attacker at `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, make `Auth::AuthScopes#initialize` and the code consuming its result disagree, given that `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal? The binding to test is SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source; the impact to prove is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
