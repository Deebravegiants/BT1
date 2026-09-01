# Q2127: initialize — asymmetric comparison via delimiter in a scope name

## Question
Is there a reachable state in which an unprivileged attacker, controlling a scope name containing `,` so one entry becomes two at `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, makes `Auth::AuthScopes#initialize` return a result the caller treats as authenticated, given that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: a scope name containing `,` so one entry becomes two
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
