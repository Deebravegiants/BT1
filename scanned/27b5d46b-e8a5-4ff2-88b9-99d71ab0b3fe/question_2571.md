# Q2571: == — no vocabulary validation via case variance

## Question
Does `Auth::AuthScopes#==` collapse two distinct identities into one when an unprivileged attacker submits scope names differing only in case, since comparison is exact string set membership at `AuthScopes#==` and `hash`, which compare only `compressed_scopes`? Show that any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: scope names differing only in case, since comparison is exact string set membership
- Exploit idea: any string is accepted as a scope, so a scope check can be satisfied by a name Shopify never issued
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
