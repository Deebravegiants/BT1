# Q507: to_signable_string — ambiguous concatenation via encoding-sensitive values

## Question
If an unprivileged attacker submits values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing) to `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, does `AuthQuery#to_signable_string` end up acting on a value that was never authenticated, because two different parameter sets serialise to the same signable string? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing)
- Exploit idea: two different parameter sets serialise to the same signable string
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
