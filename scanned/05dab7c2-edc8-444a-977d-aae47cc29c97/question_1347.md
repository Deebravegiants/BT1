# Q1347: to_signable_string — no freshness via unicode normalisation

## Question
If an unprivileged attacker submits a value that normalises differently between the browser, the framework and `URI.encode_www_form` to `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, does `AuthQuery#to_signable_string` end up acting on a value that was never authenticated, because nothing bounds the age of a signed callback, so a captured one stays valid indefinitely? Close the question on SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and on Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: a value that normalises differently between the browser, the framework and `URI.encode_www_form`
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
