# Q2859: initialize — asymmetric comparison via write_-shaped token

## Question
If an unprivileged attacker submits a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes` to `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, does `Auth::AuthScopes#initialize` end up acting on a value that was never authenticated, because `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
