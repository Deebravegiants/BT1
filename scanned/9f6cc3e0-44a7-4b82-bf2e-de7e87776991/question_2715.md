# Q2715: store_scopes — asymmetric comparison via write_-shaped token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes` at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, makes `Auth::AuthScopes#store_scopes` return a result the caller treats as authenticated, given that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
