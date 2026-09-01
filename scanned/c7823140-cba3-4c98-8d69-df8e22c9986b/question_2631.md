# Q2631: initialize — implication is textual via write_-shaped token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes` at `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, makes `Auth::AuthScopes#initialize` return a result the caller treats as authenticated, given that `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: a scope literally shaped like `write_<anything>`, which manufactures `read_<anything>` in `expanded_scopes`
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
