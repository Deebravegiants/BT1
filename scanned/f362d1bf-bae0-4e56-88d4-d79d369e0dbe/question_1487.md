# Q1487: store_scopes — equality ignores expansion via unauthenticated_ prefix

## Question
If an unprivileged attacker submits an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*` to the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, does `Auth::AuthScopes#store_scopes` end up acting on a value that was never authenticated, because `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
