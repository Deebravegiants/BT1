# Q17: initialize — implication is textual via case variance

## Question
If an unprivileged attacker submits scope names differing only in case, since comparison is exact string set membership to `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, does `Auth::AuthScopes#initialize` end up acting on a value that was never authenticated, because `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes? Close the question on SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and on Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: scope names differing only in case, since comparison is exact string set membership
- Exploit idea: `implied_scope` derives an implication from string shape alone, with no allow-list of real Shopify scopes
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
