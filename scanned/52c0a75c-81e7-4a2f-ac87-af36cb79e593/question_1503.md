# Q1503: covers? — implication is textual via write_-shaped token

## Question
Trace `Auth::AuthScopes#covers?` from `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation with a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`: because `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#covers?`
- Entrypoint: `AuthScopes#covers?(auth_scopes)`, which apps call to decide whether a session may perform an operation
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
