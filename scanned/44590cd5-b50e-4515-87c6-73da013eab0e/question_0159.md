# Q159: initialize — type confusion via encoding-sensitive values

## Question
Trace `AuthQuery#initialize` from `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string with values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing): because a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it, does the value that was verified stop being the value that is used? Prove the break against SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` and map it to Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: values whose `URI.encode_www_form` serialisation differs from the raw query string Shopify signed (spaces vs `+`, `%20`, unreserved-char casing)
- Exploit idea: a non-String value reaching the struct is stringified differently by `encode_www_form` than by the code that consumes it
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
