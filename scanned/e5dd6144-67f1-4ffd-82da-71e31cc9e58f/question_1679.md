# Q1679: implied_scope — no vocabulary validation via whitespace and empties

## Question
Is there a reachable state in which an unprivileged attacker, controlling scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied at `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope, makes `Auth::AuthScopes#implied_scope` return a result the caller treats as authenticated, given that any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#implied_scope`
- Entrypoint: `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope
- Attacker controls: scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
