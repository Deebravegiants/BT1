# Q312: to_signable_string — type confusion via oversized hmac

## Question
Can an `hmac` value of a different length or casing than the hex digest `compute_signature` produces, supplied by an unprivileged attacker at `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, make `AuthQuery#to_signable_string` and the code consuming its result disagree, given that a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: an `hmac` value of a different length or casing than the hex digest `compute_signature` produces
- Exploit idea: a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - authentication bypass: a forged or unsigned request is accepted as authentic by the app (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
