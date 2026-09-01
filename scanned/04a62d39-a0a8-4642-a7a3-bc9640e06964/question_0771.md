# Q771: to_signable_string — type confusion via host param

## Question
Starting from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, can an unprivileged attacker supply the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin so that a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `AuthQuery#to_signable_string`, and whether the result reaches Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: the base64url `host` parameter, signed but never decoded or validated as a Shopify admin origin
- Exploit idea: a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
