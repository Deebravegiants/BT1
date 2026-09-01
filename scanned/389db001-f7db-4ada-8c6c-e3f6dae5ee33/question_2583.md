# Q2583: store_scopes — asymmetric comparison via scope string from a token response

## Question
Can an unprivileged attacker reach `Auth::AuthScopes#store_scopes` through the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes` while supplying the `scope` / `associated_user_scope` strings returned with an access token and stored on the session, so that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: the `scope` / `associated_user_scope` strings returned with an access token and stored on the session
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
