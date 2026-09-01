# Q1455: store_scopes — parsing is lossy via whitespace and empties

## Question
Is there a reachable state in which an unprivileged attacker, controlling scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`, makes `Auth::AuthScopes#store_scopes` return a result the caller treats as authenticated, given that splitting and stripping can merge or drop entries so the parsed set differs from the granted grant? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
