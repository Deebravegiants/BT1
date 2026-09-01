# Q251: store_scopes — equality ignores expansion via case variance

## Question
Is there a reachable state in which an unprivileged attacker, controlling scope names differing only in case, since comparison is exact string set membership at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, makes `Auth::AuthScopes#store_scopes` return a result the caller treats as authenticated, given that `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: scope names differing only in case, since comparison is exact string set membership
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
