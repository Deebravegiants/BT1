# Q2312: implied_scope — asymmetric comparison via whitespace and empties

## Question
Does `Auth::AuthScopes#implied_scope` collapse two distinct identities into one when an unprivileged attacker submits scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied at `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope? Show that `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric, that AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#implied_scope`
- Entrypoint: `implied_scope`, whose regex `\A(unauthenticated_)?write_(.*)\z` manufactures a read scope from a write scope
- Attacker controls: scope strings with padding, empty entries or repeated delimiters, since only `strip` and `reject(&:empty?)` are applied
- Exploit idea: `covers?` compares the other side's compressed set against this side's expanded set, so the relation is not symmetric
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
