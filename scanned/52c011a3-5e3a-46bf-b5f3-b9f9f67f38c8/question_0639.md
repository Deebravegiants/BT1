# Q639: to_signable_string — no freshness via key-order dependence

## Question
Does `AuthQuery#to_signable_string` collapse two distinct identities into one when an unprivileged attacker submits a query string whose parameter order differs from the fixed hash order used in `to_signable_string` at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback? Show that nothing bounds the age of a signed callback, so a captured one stays valid indefinitely, that SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: a query string whose parameter order differs from the fixed hash order used in `to_signable_string`
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
