# Q608: initialize — equality ignores expansion via whitespace and empties

## Question
Is there a reachable state in which an unprivileged attacker, controlling scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied at `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation, makes `Auth::AuthScopes#initialize` return a result the caller treats as authenticated, given that `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal? Test AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#initialize`
- Entrypoint: `AuthScopes.new(scope_names)`, which splits a string on `,` with no token validation
- Attacker controls: scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
