# Q2667: initialize — implication is textual via compressed vs expanded asymmetry

## Question
Can an unprivileged attacker reach `Auth::AuthScopes#initialize` through `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation while supplying a comparison where the caller's required scopes are compressed and the session's are expanded, so that `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes, breaking the requirement that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source, and ending in High - scope or expiry check bypass granting an operation the session was never authorized for?

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: a comparison where the caller's required scopes are compressed and the session's are expanded
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
