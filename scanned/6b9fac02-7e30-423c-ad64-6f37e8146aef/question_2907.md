# Q2907: store_scopes — equality ignores expansion via delimiter in a scope name

## Question
Does `Auth::AuthScopes#store_scopes` collapse two distinct identities into one when an unprivileged attacker submits a scope name containing `,` so one entry becomes two at the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`? Show that `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is High - scope or expiry check bypass granting an operation the session was never authorized for.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#store_scopes`
- Entrypoint: the private `store_scopes`, which builds `compressed_scopes` and `expanded_scopes`
- Attacker controls: a scope name containing `,` so one entry becomes two
- Exploit idea: `==` and `hash` use only `compressed_scopes`, so two sets with different effective permissions compare equal
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - scope or expiry check bypass granting an operation the session was never authorized for (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert `covers?` is false for any scope name outside a known Shopify scope vocabulary
